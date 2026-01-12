import json
import time
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.crud import book as crud_book
from app.crud import game as crud_game
from app.crud import recommendation as crud_recommendation
from app.schemas.book import BookCreate
from app.schemas.game import GameCreate
from app.services.cache_service import cache_service
from app.services.external import google_books_service, huggingface_service
from app.services.ai_game_generator import ai_game_generator

logger = get_logger()


class RecommendationService:
    """
    Serviço de recomendação de jogos baseados em livros usando IA.
    
    Pipeline Otimizado:
    1. extract_book_features: Extrai categorias, tema, autor do Google Books
    2. map_genres_to_tags: Mapeia categorias do Google Books → tags de jogos
    3. search_similar_games: Gera jogos completos usando Llama 3.1 8B Instruct
    4. calculate_similarity_score: Calcula score de similaridade
    5. save_recommendation: Salva no banco e cache (24h)
    
    Otimizações:
    - ✅ Removida classificação AI redundante (ProsusAI/finbert)
    - ✅ Usa categorias do Google Books diretamente (mais rápido)
    - ✅ Llama 3.1 gera dados completos dos jogos (não mais random)
    """

    # Mapeamento manual de gêneros literários → tags de jogos
    GENRE_TAG_MAPPING = {
        "fantasy": ["fantasy", "magic", "dragons", "medieval"],
        "science fiction": ["sci-fi", "space", "futuristic", "cyberpunk"],
        "adventure": ["adventure", "exploration", "open-world"],
        "mystery": ["mystery", "detective", "crime", "investigation"],
        "thriller": ["thriller", "suspense", "psychological"],
        "horror": ["horror", "survival-horror", "dark", "gore"],
        "romance": ["romance", "dating-sim", "story-rich"],
        "historical": ["historical", "realistic", "war"],
        "action": ["action", "combat", "fast-paced"],
        "drama": ["drama", "story-rich", "emotional"],
        "comedy": ["comedy", "funny", "casual"],
        "dystopian": ["post-apocalyptic", "dystopian", "survival"],
        "post-apocalyptic": ["post-apocalyptic", "survival", "zombies"],
        "superhero": ["superhero", "super-powers", "comic-book"],
        "crime": ["crime", "mafia", "heist"],
        "war": ["war", "military", "tactical"],
        "magic": ["magic", "spells", "wizards"],
        "dark": ["dark", "dark-fantasy", "mature"],
        "epic": ["epic", "grand-strategy", "story-rich"],
    }

    def extract_book_features(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai características relevantes do livro.
        
        Args:
            book_data: Dados do livro (Google Books format)
            
        Returns:
            Features extraídas
        """
        volume_info = book_data.get("volumeInfo", {})
        
        features = {
            "title": volume_info.get("title", ""),
            "authors": volume_info.get("authors", []),
            "description": volume_info.get("description", ""),
            "categories": volume_info.get("categories", []),
            "published_year": volume_info.get("publishedDate", "")[:4] if volume_info.get("publishedDate") else None,
            "language": volume_info.get("language", "en"),
            "page_count": volume_info.get("pageCount"),
        }
        
        logger.info(f"Extracted features from book: {features['title']}")
        return features



    def map_genres_to_tags(
        self,
        book_features: Dict[str, Any],
    ) -> List[str]:
        """
        Mapeia categorias do Google Books para tags de jogos.
        
        Args:
            book_features: Features do livro com categorias
            
        Returns:
            Lista de tags de jogos
        """
        tags = []
        
        # Usar categorias do Google Books diretamente
        categories = book_features.get("categories", [])
        
        for category in categories:
            category_lower = category.lower()
            for genre, genre_tags in self.GENRE_TAG_MAPPING.items():
                if genre in category_lower:
                    tags.extend(genre_tags)
                    break
        
        # Remove duplicatas
        tags = list(set(tags))
        
        # Se não tem tags das categorias, usar descrição e título
        if not tags:
            description_lower = book_features.get("description", "").lower()
            title_lower = book_features.get("title", "").lower()
            combined_text = f"{title_lower} {description_lower}"
            
            for genre, genre_tags in self.GENRE_TAG_MAPPING.items():
                if genre in combined_text:
                    tags.extend(genre_tags[:2])
                    if len(tags) >= 10:
                        break
        
        # Último recurso: keywords específicas
        if not tags:
            keywords_map = {
                "technology": ["sci-fi", "cyberpunk", "simulation"],
                "business": ["strategy", "management", "simulation"],
                "war": ["war", "strategy", "military"],
                "history": ["historical", "strategy"],
                "space": ["space", "sci-fi", "exploration"],
                "crime": ["crime", "action", "thriller"],
                "spy": ["stealth", "action", "thriller"],
                "detective": ["mystery", "detective", "investigation"],
            }
            
            combined_text = f"{book_features.get('title', '').lower()} {book_features.get('description', '').lower()}"
            
            for keyword, keyword_tags in keywords_map.items():
                if keyword in combined_text:
                    tags.extend(keyword_tags[:2])
            
            # Tags genéricas se nada funcionar
            if not tags:
                tags = ["story-rich", "adventure", "singleplayer"]
                logger.warning(f"No specific tags found, using generic tags: {tags}")
        
        # Remove duplicatas e limita a 10 tags
        tags = list(set(tags))[:10]
        
        logger.info(f"Generated tags from Google Books: {tags}")
        return tags

    async def search_similar_games(
        self,
        tags: List[str],
        book_title: str = "",
        book_description: str = "",
        page_size: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Gera jogos usando IA baseado nas tags (sem APIs externas).
        
        Args:
            tags: Tags para geração
            book_title: Título do livro para contexto
            book_description: Descrição do livro
            page_size: Número de jogos a gerar
            
        Returns:
            Lista de jogos gerados pela IA
        """
        if not tags:
            logger.warning("No tags provided for game generation")
            return []
        
        # Gera jogos usando IA Llama 3.1 8B Instruct
        games = await ai_game_generator.generate_games(
            tags=tags,
            book_title=book_title,
            book_description=book_description,
            count=page_size,
        )
        
        logger.info(f"Generated {len(games)} AI games matching tags: {tags}")
        return games

    def calculate_similarity_score(
        self,
        game: Dict[str, Any],
        book_features: Dict[str, Any],
        matched_tags: List[str],
    ) -> float:
        """
        Calcula score de similaridade entre livro e jogo.
        
        Args:
            game: Dados do jogo
            book_features: Features do livro
            matched_tags: Tags que combinaram
            
        Returns:
            Score de 0.0 a 1.0
        """
        score = 0.0
        
        # Base score: rating do jogo (normalizado)
        game_rating = game.get("rating") or 0
        if game_rating > 0:
            score += (game_rating / 5.0) * 0.3
        
        # Tag matching score
        # Suporta tags AI-generated (string ou list of strings)
        tags_raw = game.get("tags", [])
        if isinstance(tags_raw, str):
            game_tags = [tag.strip() for tag in tags_raw.split(",")]
        elif isinstance(tags_raw, list) and len(tags_raw) > 0:
            # AI format: ["fantasy", "magic", ...]
            game_tags = tags_raw
        else:
            game_tags = []
        
        if matched_tags and len(matched_tags) > 0:
            matched_count = sum(1 for tag in matched_tags if tag in game_tags)
            tag_score = matched_count / len(matched_tags)
            score += min(tag_score, 1.0) * 0.5
        
        # Popularity score (metacritic)
        metacritic = game.get("metacritic") or 0
        if metacritic > 0:
            popularity_score = metacritic / 100.0
            score += min(popularity_score, 1.0) * 0.2
        
        return round(min(score, 1.0), 2)

    async def generate_recommendation(
        self,
        db: Session,
        user_id: int,
        book_id: int,  # Internal book ID (not Google Books ID)
    ) -> Dict[str, Any]:
        """
        Gera recomendação completa de jogos para um livro.
        
        Args:
            db: Database session
            user_id: ID do usuário
            book_id: Internal book ID (integer from database)
            
        Returns:
            Recommendation data com games e metadata
        """
        start_time = time.time()
        
        # Check cache primeiro (recomendação completa)
        cache_key = f"recommendation:book:{book_id}"
        cached = cache_service.get(cache_key)
        if cached:
            logger.info(f"Recommendation cache HIT for book {book_id}")
            
            # Save to user's history even if cached
            db_recommendation = crud_recommendation.create_recommendation(
                db=db,
                user_id=user_id,
                book_id=book_id,
                games=cached["games_json"],
                ai_generated=cached["ai_generated"],
                similarity_score=cached["similarity_score"],
                processing_time_ms=cached["processing_time_ms"],
            )
            
            # Get book data
            db_book = crud_book.get_book(db, book_id)
            book_data = await google_books_service.get_details(db_book.google_books_id)
            parsed_book = google_books_service.parse_book_data(book_data)
            
            # Return with recommendation object for consistency
            return {
                "recommendation": db_recommendation,
                "book_data": parsed_book,
                "games": cached["games"],
            }
        
        logger.info(f"Recommendation cache MISS for book {book_id}, generating...")
        
        # 1. Get book from database to obtain google_books_id
        db_book = crud_book.get_book(db, book_id)
        if not db_book:
            raise ValueError(f"Book with ID {book_id} not found in database")
        
        # 2. Get book details from Google Books API using google_books_id
        book_data = await google_books_service.get_details(db_book.google_books_id)
        if not book_data:
            raise ValueError(f"Book not found in Google Books API: {db_book.google_books_id}")
        
        # Parse book data for response
        parsed_book = google_books_service.parse_book_data(book_data)
        
        # 3. Extract features
        book_features = self.extract_book_features(book_data)
        
        # 4. Map Google Books categories to game tags
        tags = self.map_genres_to_tags(book_features)
        
        # 5. Generate similar games using Llama 3.1 (with complete data)
        games = await self.search_similar_games(
            tags=tags,
            book_title=book_features.get("title", ""),
            book_description=book_features.get("description", ""),
            page_size=5,
        )
        
        # 7. Calculate similarity scores and select top games
        game_recommendations = []
        for game in games[:10]:  # Top 10 games
            try:
                score = self.calculate_similarity_score(game, book_features, tags)
                if score >= 0.5:  # Threshold mínimo
                    game_recommendations.append({
                        "game_id": game.get("id"),
                        "name": game.get("name", "Unknown"),
                        "score": score,
                        "rating": game.get("rating"),
                        "image": game.get("image_url"),
                    })
            except Exception as e:
                logger.error(f"Error calculating score for game {game.get('name', 'unknown')}: {e}")
                logger.error(f"Game data: {game}")
                continue
        
        # Sort by score
        game_recommendations.sort(key=lambda x: x["score"], reverse=True)
        game_recommendations = game_recommendations[:5]  # Top 5
        
        # Validar se encontrou jogos
        if not game_recommendations:
            logger.warning(f"No game recommendations found for book {db_book.id} with tags: {tags}")
            raise ValueError(
                f"Could not find suitable games for this book. "
                f"Try a book with more defined genre (fantasy, sci-fi, adventure, etc.)"
            )
        
        # Calculate overall similarity score
        avg_score = sum(g["score"] for g in game_recommendations) / len(game_recommendations)
        
        # 7. Save Llama-generated games to database
        for game_rec in game_recommendations:
            # Busca o jogo completo gerado pela IA
            game_full_data = next((g for g in games if g.get("id") == game_rec.get("game_id")), None)
            if game_full_data:
                try:
                    # Valida dados obrigatórios
                    rawg_id = game_full_data.get("rawg_id")
                    if not rawg_id:
                        logger.error(f"Game {game_full_data.get('name')} has no rawg_id, skipping")
                        continue
                    
                    logger.info(f"Saving game: {game_full_data.get('name')} (ID: {game_full_data.get('id')})")
                    
                    # Cria GameCreate a partir dos dados gerados
                    game_create = GameCreate(
                        rawg_id=rawg_id,
                        name=game_full_data.get("name"),
                        slug=game_full_data.get("slug"),
                        description=game_full_data.get("description"),
                        released=game_full_data.get("released"),
                        rating=game_full_data.get("rating"),
                        ratings_count=game_full_data.get("ratings_count"),
                        metacritic=game_full_data.get("metacritic"),
                        playtime=game_full_data.get("playtime"),
                        genres=game_full_data.get("genres"),
                        tags=game_full_data.get("tags"),
                        platforms=game_full_data.get("platforms"),
                        developers=game_full_data.get("developers"),
                        publishers=game_full_data.get("publishers"),
                        image_url=game_full_data.get("image_url"),
                        website=game_full_data.get("website"),
                    )
                    crud_game.get_or_create_game(db, game_create)
                    logger.info(f"Game saved successfully: {game_full_data.get('name')}")
                except Exception as e:
                    logger.error(f"Error saving game {game_full_data.get('name')}: {e}")
                    logger.error(f"Game data: {game_full_data}")
                    # NÃO faz raise - continua com os outros jogos
                    continue
            else:
                logger.warning(f"Game not found in full data: {game_rec.get('game_id')}")
        
        # Save recommendation
        games_json = json.dumps([{"game_id": g["game_id"], "score": g["score"]} for g in game_recommendations])
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        db_recommendation = crud_recommendation.create_recommendation(
            db=db,
            user_id=user_id,
            book_id=db_book.id,
            games=games_json,
            ai_generated=True,  # Sempre True (Llama gera tudo)
            similarity_score=round(avg_score, 2),
            processing_time_ms=processing_time_ms,
        )
        
        logger.info(
            f"Recommendation generated in {processing_time_ms}ms "
            f"(Llama: True, Score: {avg_score:.2f}, Games: {len(game_recommendations)})"
        )
        
        # Cache result (for future cache hits)
        cache_data = {
            "games": game_recommendations,
            "games_json": games_json,
            "ai_generated": True,
            "similarity_score": round(avg_score, 2),
            "processing_time_ms": processing_time_ms,
            "tags_used": tags,
        }
        
        cache_service.set(cache_key, cache_data)
        
        # Return with recommendation object for consistency
        return {
            "recommendation": db_recommendation,
            "book_data": parsed_book,
            "games": game_recommendations,
        }


# Singleton instance
recommendation_service = RecommendationService()
