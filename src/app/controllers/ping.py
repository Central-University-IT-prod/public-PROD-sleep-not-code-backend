from litestar import get


@get("/api/ping")
async def ping() -> None:
    return
