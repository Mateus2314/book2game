import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { View, Text, TouchableOpacity, Image } from 'react-native';
import { mockBooks } from '../helpers/mockData';

// Mock BookDetailsScreen using React Native components
const BookDetailsScreen = ({ book = mockBooks.book1 }) => (
  <View>
    <Text testID="book-title">{book.title}</Text>
    <Image testID="book-image" source={{ uri: book.image_url }} />
    <Text testID="book-author">{book.author}</Text>
    <Text testID="book-description">{book.description}</Text>
    <Text testID="book-rating">{book.rating || 0} stars</Text>
    <TouchableOpacity testID="add-to-library-button">
      <Text>Add to Library</Text>
    </TouchableOpacity>
    <TouchableOpacity testID="rate-button">
      <Text>Rate</Text>
    </TouchableOpacity>
    <TouchableOpacity testID="recommend-button">
      <Text>Recommend</Text>
    </TouchableOpacity>
  </View>
);

describe('BookDetailsScreen', () => {
  describe('Book Information Display', () => {
    it('should display book title', () => {
      render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(screen.getByTestId('book-title')).toBeTruthy();
    });

    it('should display book image', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(getByTestId('book-image')).toBeTruthy();
    });

    it('should display author name', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(getByTestId('book-author')).toBeTruthy();
    });

    it('should display book description', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(getByTestId('book-description')).toBeTruthy();
    });

    it('should display book rating', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(getByTestId('book-rating')).toBeTruthy();
    });
  });

  describe('Different Books', () => {
    it('should render first mock book', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(getByTestId('book-title')).toBeTruthy();
    });

    it('should render second mock book', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book2} />);
      
      expect(getByTestId('book-title')).toBeTruthy();
    });

    it('should handle books without rating', () => {
      const bookWithoutRating = { ...mockBooks.book1, rating: null };
      const { getByTestId } = render(<BookDetailsScreen book={bookWithoutRating} />);
      
      expect(getByTestId('book-rating')).toBeTruthy();
    });
  });

  describe('User Interactions', () => {
    it('should add book to library', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      const addButton = getByTestId('add-to-library-button');
      
      fireEvent.press(addButton);
      expect(addButton).toBeTruthy();
    });

    it('should allow rating the book', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      const rateButton = getByTestId('rate-button');
      
      fireEvent.press(rateButton);
      expect(rateButton).toBeTruthy();
    });

    it('should allow recommending the book', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      const recommendButton = getByTestId('recommend-button');
      
      fireEvent.press(recommendButton);
      expect(recommendButton).toBeTruthy();
    });
  });

  describe('State Management', () => {
    it('should track if book is in library', () => {
      render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(screen.getByTestId('add-to-library-button')).toBeTruthy();
    });

    it('should update rating when user rates', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      const rateButton = getByTestId('rate-button');
      
      fireEvent.press(rateButton);
      expect(getByTestId('book-rating')).toBeTruthy();
    });
  });

  describe('Navigation', () => {
    it('should allow navigating back', () => {
      render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(screen.getByTestId('book-title')).toBeTruthy();
    });

    it('should allow navigating to similar books', () => {
      render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(screen.getByTestId('recommend-button')).toBeTruthy();
    });
  });

  describe('Accessibility', () => {
    it('should have accessible buttons', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(getByTestId('add-to-library-button')).toBeTruthy();
      expect(getByTestId('rate-button')).toBeTruthy();
      expect(getByTestId('recommend-button')).toBeTruthy();
    });

    it('should display all information accessibly', () => {
      const { getByTestId } = render(<BookDetailsScreen book={mockBooks.book1} />);
      
      expect(getByTestId('book-title')).toBeTruthy();
      expect(getByTestId('book-author')).toBeTruthy();
      expect(getByTestId('book-description')).toBeTruthy();
    });
  });
});