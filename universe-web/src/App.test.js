import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from './App';

function mockApi() {
  global.fetch = jest.fn((url) => {
    if (url === '/user/login') {
      return Promise.resolve({
        ok: true,
        json: async () => ({ id: 1, username: 'student' }),
      });
    }

    if (url === '/upload/get_topics') {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          success: true,
          topics: [{ name: 'Math', description: 'Math notes' }],
        }),
      });
    }

    if (url === '/upload/new_document') {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          success: true,
          topic: 'Math',
          filename: 'notes.txt',
          content_type: 'text/plain',
          size_mb: 0.01,
          document_id: 1,
          num_chunks: 1,
          concepts: 'notes',
        }),
      });
    }

    if (url === '/upload/new_topic') {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          success: true,
          name: 'Science',
          description: 'Science notes',
        }),
      });
    }

    return Promise.resolve({ ok: true, json: async () => ({}) });
  });
}

async function login() {
  fireEvent.change(screen.getByLabelText(/username/i), {
    target: { value: 'student' },
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'password' },
  });
  fireEvent.click(screen.getByRole('button', { name: /^login$/i }));

  await waitFor(() => {
    expect(screen.getByText(/signed in as student/i)).toBeInTheDocument();
  });
}

beforeEach(() => {
  mockApi();
});

test('opens the topic universe after login', async () => {
  render(<App />);

  expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();

  await login();

  expect(screen.getByText(/signed in as student/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /create topic/i })).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /upload your notes/i })).not.toBeInTheDocument();
});

test('creates a new topic', async () => {
  render(<App />);

  await login();

  fireEvent.change(screen.getByPlaceholderText(/topic name/i), {
    target: { value: 'Science' },
  });
  fireEvent.change(screen.getByPlaceholderText(/topic description/i), {
    target: { value: 'Science notes' },
  });
  fireEvent.click(screen.getByRole('button', { name: /create topic/i }));

  await waitFor(() => {
    expect(screen.getByText(/created topic: science/i)).toBeInTheDocument();
  });

  expect(fetch).toHaveBeenCalledWith(
    '/upload/new_topic',
    expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({
        name: 'Science',
        description: 'Science notes',
      }),
    })
  );
});

test('does not render a central upload dialog', async () => {
  render(<App />);

  await login();

  expect(screen.queryByRole('button', { name: /upload your notes/i })).not.toBeInTheDocument();
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});
