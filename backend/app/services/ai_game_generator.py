"""
Serviço para gerar recomendações de jogos REAIS usando Llama 3.1 8B Instruct via Hugging Face.
"""
import hashlib
import random
from typing import Any, Dict, List

from app.core.logging import get_logger

logger = get_logger()


class AIGameGenerator:
    """Gera recomendações de jogos REAIS usando IA (Llama 3.1)."""

    TAG_TO_GENRE_MAP = {
        "fantasy": ["RPG", "Action RPG", "Adventure"],
        "sci-fi": ["Shooter", "Action", "RPG"],
        "action": ["Action", "Shooter", "Fighting"],
        "horror": ["Horror", "Survival", "Action"],
        "adventure": ["Adventure", "Action-Adventure", "Platformer"],
        "open-world": ["Open World", "RPG", "Action"],
        "story-rich": ["Narrative", "Adventure", "RPG"],
        "magic": ["RPG", "Fantasy", "Action RPG"],
        "shooter": ["Shooter", "FPS", "Action"],
        "strategy": ["Strategy", "Simulation", "Management"],
    }

    def _generate_unique_id(self, game_name: str) -> int:
        """
        Gera ID único e consistente baseado no nome do jogo.
        Mesmo jogo sempre gera o mesmo ID.
        Garante que o valor cabe em PostgreSQL INTEGER (max: 2^31-1).
        """
        hash_obj = hashlib.md5(game_name.lower().encode())
        # Usa 7 caracteres (28 bits) para garantir < 2^31-1
        hash_int = int(hash_obj.hexdigest()[:7], 16)
        # Segurança adicional: garante que é positivo e < 2^31
        return hash_int % 2147483647

    def _clean_markdown(self, text: str) -> str:
        """
        Remove marcações markdown (bold, italic) do texto.
        Llama pode retornar: **Game Name** ou *Game Name*
        """
        import re
        # Remove **bold** e *italic*
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **text** → text
        text = re.sub(r'\*(.+?)\*', r'\1', text)      # *text* → text
        text = re.sub(r'__(.+?)__', r'\1', text)      # __text__ → text
        text = re.sub(r'_(.+?)_', r'\1', text)        # _text_ → text
        return text.strip()

    async def generate_games(
        self,
        tags: List[str],
        book_title: str,
        book_description: str,
        count: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Gera jogos REAIS usando Llama 3.1 8B Instruct.
        Fallback para templates se Llama falhar.

        Args:
            tags: Tags extraídas do livro
            book_title: Título do livro para contexto
            book_description: Descrição do livro
            count: Número de jogos a gerar

        Returns:
            Lista de jogos gerados
        """
        logger.info(f"Generating {count} games for tags: {tags}")

        # Usa APENAS Llama 
        games = await self._generate_with_llama(tags, count)
        
        if not games or len(games) < count:
            logger.error(f"Llama failed to generate {count} games. Got {len(games) if games else 0}.")
            raise ValueError(f"Failed to generate {count} games via Llama AI. Please check Hugging Face API status.")
        
        logger.info(f"Successfully generated {len(games)} games via Llama")
        return games

    async def _generate_with_llama(self, tags: List[str], count: int) -> List[Dict[str, Any]]:
        """
        Usa Llama 3.1 para gerar dados COMPLETOS de jogos reais.
        
        Args:
            tags: Tags do livro
            count: Número de jogos a gerar
            
        Returns:
            Lista de jogos com dados completos da IA
        """
        from app.services.external import huggingface_service
        
        tags_str = ", ".join(tags[:3])
        
        # Prompt otimizado para retornar dados estruturados
        prompt = f"""List {count} real popular video games about {tags_str}.

For each game provide:
- Name
- Release year
- Rating (0-5)
- Genre
- Brief description (1 sentence)

Format:
1. [Name] ([Year]) - Rating: [X.X]/5 - Genre: [Genre] - [Description]"""
        
        # Chama Llama via Chat Completions com mais tokens
        result = await huggingface_service.generate_text_with_llama(
            prompt=prompt,
            max_tokens=800  # Mais tokens para dados completos
        )
        
        if not result:
            raise ValueError("Llama returned empty response")
        
        # Log resposta completa para debug
        logger.info(f"Llama raw response (first 500 chars): {result[:500]}")
        
        # Parse dados estruturados
        games = self._parse_structured_games(result, tags)
        
        if not games:
            logger.error(f"Failed to parse any games from Llama response: {result[:200]}")
            raise ValueError(f"Failed to parse games from Llama. Response format may be invalid.")
        
        if len(games) < count:
            logger.warning(f"Parsed only {len(games)}/{count} games from Llama")
        
        # Log jogos gerados para debug
        for i, game in enumerate(games[:count]):
            logger.info(f"Game {i+1}: {game.get('name')} | ID: {game.get('id')} | Rating: {game.get('rating')}")
        
        return games[:count]

    def _parse_structured_games(self, ai_response: str, tags: List[str]) -> List[Dict[str, Any]]:
        """Parse resposta estruturada da IA com dados completos dos jogos."""
        import re
        
        lines = ai_response.strip().split("\n")
        games = []
        
        # Pattern: 1. Game Name (2015) - Rating: 4.5/5 - Genre: RPG - Description
        pattern = r"^\d+\.\s*(.+?)\s*\((\d{4})\)\s*-\s*Rating:\s*([\d.]+).*?-\s*Genre:\s*([^-]+)\s*-\s*(.+)$"
        
        # Patterns de linhas a ignorar (introduções do Llama)
        ignore_patterns = [
            r"^here are \d+ (popular|real|video games)",
            r"^i (recommend|suggest|present)",
            r"^below (is|are) (some|the)",
            r"^based on your",
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Ignora linhas de introdução
            line_lower = line.lower()
            if any(re.match(pattern, line_lower) for pattern in ignore_patterns):
                logger.info(f"Skipping intro line: {line[:50]}...")
                continue
                
            match = re.match(pattern, line, re.IGNORECASE)
            
            if match:
                name = self._clean_markdown(match.group(1).strip())  # Remove markdown
                year = match.group(2)
                rating = float(match.group(3))
                genre = self._clean_markdown(match.group(4).strip())  # Remove markdown
                description = self._clean_markdown(match.group(5).strip())  # Remove markdown
                
                game = self._create_game_from_llama_data(
                    name=name,
                    year=year,
                    rating=min(rating, 5.0),  # Normaliza rating
                    genre=genre,
                    description=description,
                    tags=tags,
                    index=i
                )
                games.append(game)
            else:
                # Fallback: extrai apenas o nome
                cleaned = line.lstrip("0123456789.-• ").strip()
                
                # Ignora linhas muito curtas ou que parecem introdução
                if len(cleaned) < 3 or ':' in cleaned:
                    continue
                    
                if cleaned and len(cleaned) > 2:
                    # Extrai nome até parêntese
                    name_match = re.match(r"^([^(]+)", cleaned)
                    if name_match:
                        name = self._clean_markdown(name_match.group(1).strip())  # Remove markdown
                        
                        # Valida que é um nome de jogo válido
                        if len(name) > 3 and not name.lower().startswith(('here', 'below', 'i recommend')):
                            game = self._create_game_from_real_name(name, tags, i)
                            games.append(game)
        
        return games

    def _create_game_from_llama_data(
        self,
        name: str,
        year: str,
        rating: float,
        genre: str,
        description: str,
        tags: List[str],
        index: int
    ) -> Dict[str, Any]:
        """
        Cria estrutura de jogo usando dados REAIS fornecidos pela Llama.
        """
        # ID único baseado no NOME (consistente)
        game_id = self._generate_unique_id(name)
        
        # Converte rating para escala 0-5
        normalized_rating = min(max(rating, 0.0), 5.0)
        
        # Metacritic baseado no rating (aproximação: 4.5 → 90)
        metacritic = int(normalized_rating * 20) if normalized_rating > 0 else None
        
        # Slug do nome
        slug = name.lower().replace(" ", "-").replace(":", "").replace("'", "").replace(",", "")
        
        # Ratings count baseado no rating (jogos melhores = mais avaliações)
        ratings_count = int(normalized_rating * 50000) if normalized_rating > 0 else 10000
        
        return {
            "id": game_id,
            "rawg_id": game_id,  # Mesmo ID (campo obrigatório do banco)
            "name": name,
            "slug": slug,
            "description": description,  # ✅ Da IA
            "released": f"{year}-01-01",  # ✅ Da IA (ano)
            "rating": round(normalized_rating, 2),  # ✅ Da IA
            "ratings_count": ratings_count,  # Calculado do rating
            "metacritic": metacritic,  # Calculado do rating
            "playtime": None,  # ❌ Llama não fornece
            "genres": genre,  # ✅ Da IA
            "tags": ", ".join(tags[:5]),
            "platforms": None,  # ❌ Llama não fornece
            "developers": None,  # ❌ Llama não fornece
            "publishers": None,  # ❌ Llama não fornece
            "image_url": None,  # ❌ Sem API de imagens
            "website": None,  # ❌ Llama não fornece
        }

    def _create_game_from_real_name(
        self,
        name: str,
        tags: List[str],
        index: int
    ) -> Dict[str, Any]:
        """
        Fallback: Cria estrutura de jogo apenas com o nome (quando parse da IA falha).
        """
        # ID único baseado no NOME
        game_id = self._generate_unique_id(name)
        
        # Seleciona categoria principal
        primary_category = self._select_primary_category(tags)
        
        # Rating estimado para jogos populares
        rating = round(random.uniform(3.8, 4.9), 2)
        
        # Ano aleatório recente
        year = random.randint(2015, 2024)
        released = f"{year}-01-01"
        
        # Mapeia tags para gêneros
        genres = self._generate_genres(tags, primary_category)
        
        # Descrição genérica
        description = f"{name} is a critically acclaimed {', '.join(genres)} game that combines {', '.join(tags[:3])} themes."
        
        # Slug do nome
        slug = name.lower().replace(" ", "-").replace(":", "").replace("'", "").replace(",", "")
        
        return {
            "id": game_id,
            "name": name,
            "slug": slug,
            "description": description,
            "released": released,
            "rating": rating,
            "ratings_count": int(rating * 40000),
            "metacritic": int(rating * 20),
            "playtime": None,
            "genres": ", ".join(genres),
            "tags": ", ".join(tags[:5]),
            "platforms": None,
            "developers": None,
            "publishers": None,
            "image_url": None,
            "website": None,
        }

    def _select_primary_category(self, tags: List[str]) -> str:
        """Seleciona a categoria principal baseada nas tags."""
        priority = ["fantasy", "sci-fi", "horror", "action", "adventure"]
        
        for category in priority:
            if category in tags:
                return category
        
        return "adventure"  # Default

    def _generate_genres(self, tags: List[str], primary_category: str) -> List[str]:
        """Mapeia tags para gêneros de jogos."""
        genres = set()
        
        # Adiciona gêneros da categoria principal
        if primary_category in self.TAG_TO_GENRE_MAP:
            genres.update(self.TAG_TO_GENRE_MAP[primary_category][:2])
        
        # Adiciona gêneros de outras tags
        for tag in tags[:3]:
            if tag in self.TAG_TO_GENRE_MAP:
                genres.add(self.TAG_TO_GENRE_MAP[tag][0])
        
        return list(genres)[:3]  # Máximo 3 gêneros


# Instância global
ai_game_generator = AIGameGenerator()
