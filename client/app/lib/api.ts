export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function responseMessage(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string };
    return data.detail ?? `Request failed (${response.status})`;
  } catch {
    return `Request failed (${response.status})`;
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(await responseMessage(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function csrfToken(): Promise<string> {
  const data = await apiFetch<{ csrfToken: string }>("/api/auth/csrf/");
  return data.csrfToken;
}

export async function apiPost<T>(path: string): Promise<T> {
  const token = await csrfToken();
  return apiFetch<T>(path, {
    method: "POST",
    headers: {
      "X-CSRFToken": token,
      "Content-Type": "application/json",
    },
    body: "{}",
  });
}
