
export default async function handler(request) {
  if (request.method !== "GET") {
    return Response.json(
      { error: "Method not allowed" },
      { status: 405 }
    );
  }

  const configuredToken = process.env.ADMIN_API_TOKEN;

  return Response.json({
    status: "ok",
    token_configured: Boolean(configuredToken),
    message: configuredToken
      ? "認証設定を確認しました"
      : "認証トークンが未設定です"
  });
}
