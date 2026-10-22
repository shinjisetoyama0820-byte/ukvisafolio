
import { timingSafeEqual } from "node:crypto";

export default async function handler(request) {
  if (request.method !== "POST") {
    return Response.json(
      { error: "Method not allowed" },
      { status: 405 }
    );
  }

  const expected = process.env.ADMIN_API_TOKEN;
  const authorization = request.headers.get("Authorization") || "";
  const prefix = "Bearer ";

  if (!expected || !authorization.startsWith(prefix)) {
    return Response.json(
      { authenticated: false },
      { status: 401 }
    );
  }

  const received = authorization.slice(prefix.length);
  const a = Buffer.from(received);
  const b = Buffer.from(expected);

  const valid =
    a.length === b.length &&
    timingSafeEqual(a, b);

  return Response.json(
    { authenticated: valid },
    {
      status: valid ? 200 : 401,
      headers: { "Cache-Control": "no-store" }
    }
  );
}
