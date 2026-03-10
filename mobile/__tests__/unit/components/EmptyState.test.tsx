import React from 'react';
import { screen, render } from '@testing-library/react-native';
import { EmptyState } from '@/components/common/EmptyState';

describe('EmptyState', () => {
  describe('Required Props', () => {
    it('should render with required props only', () => {
      render(
        <EmptyState icon="inbox-outline" title="Empty Inbox" />
      );

      expect(screen.getByText('Empty Inbox')).toBeTruthy();
    });

    it('should render title correctly', () => {
      render(
        <EmptyState icon="home-outline" title="Hello World" />
      );

      expect(screen.getByText('Hello World')).toBeTruthy();
    });
  });

  describe('Optional Description', () => {
    it('should render description when provided', () => {
      render(
        <EmptyState 
          icon="inbox-outline" 
          title="No Items" 
          description="Try adding something new"
        />
      );

      expect(screen.getByText('No Items')).toBeTruthy();
      expect(screen.getByText('Try adding something new')).toBeTruthy();
    });

    it('should render empty state with only title and icon when no description', () => {
      render(
        <EmptyState icon="test-icon" title="Test Title" />
      );

      expect(screen.getByText('Test Title')).toBeTruthy();
    });
  });

  describe('Accessibility', () => {
    it('should be accessible', () => {
      const { getByText } = render(
        <EmptyState icon="inbox-outline" title="Accessible" />
      );

      expect(getByText('Accessible')).toBeTruthy();
    });
  });
});