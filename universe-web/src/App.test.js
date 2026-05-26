import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from './App';

function login() {
  fireEvent.change(screen.getByLabelText(/username/i), {
    target: { value: 'student' },
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'password' },
  });
  fireEvent.click(screen.getByRole('button', { name: /^login$/i }));
}

test('opens the upload screen after login', () => {
  render(<App />);

  expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();

  login();

  expect(screen.getByText(/signed in as student/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /upload your notes/i })).toBeInTheDocument();
});

test('shows a star image after a successful file upload', async () => {
  global.fetch = jest.fn().mockResolvedValue({ ok: true });
  render(<App />);

  login();
  fireEvent.click(screen.getByRole('button', { name: /upload your notes/i }));

  expect(screen.getByRole('dialog', { name: /upload your notes/i })).toBeInTheDocument();

  fireEvent.change(screen.getByLabelText(/choose file/i), {
    target: { files: [new File(['notes'], 'notes.txt', { type: 'text/plain' })] },
  });

  await waitFor(() => {
    expect(screen.getByText(/file uploaded successfully/i)).toBeInTheDocument();
    expect(screen.getByAltText('Star')).toBeInTheDocument();
  });

  expect(fetch).toHaveBeenCalledWith(
    '/api/upload/',
    expect.objectContaining({ method: 'POST', body: expect.any(FormData) })
  );
});

test('closes the upload popup', () => {
  render(<App />);

  login();
  fireEvent.click(screen.getByRole('button', { name: /upload your notes/i }));
  fireEvent.click(screen.getByRole('button', { name: /close/i }));

  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});
