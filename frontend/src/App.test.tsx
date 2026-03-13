import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Login from './pages/Login';

test('renders login form', () => {
  render(
    <MemoryRouter>
      <Login />
    </MemoryRouter>
  );
  expect(screen.getByText(/NSCT Portal/i)).toBeInTheDocument();
  expect(screen.getByPlaceholderText(/focal@university.edu/i)).toBeInTheDocument();
});
