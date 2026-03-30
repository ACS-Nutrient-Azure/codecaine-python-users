import asyncio
from app.db.database import engine
from sqlalchemy import text

async def fix():
    async with engine.begin() as conn:
        # 1. 삭제할 cognito_id 목록 조회 (email별 가장 오래된 것 제외)
        result = await conn.execute(text("""
            SELECT cognito_id FROM users
            WHERE cognito_id NOT IN (
                SELECT DISTINCT ON (email) cognito_id
                FROM users
                ORDER BY email, created_at ASC
            )
        """))
        to_delete = [row[0] for row in result.fetchall()]
        print(f"삭제할 cognito_id: {to_delete}")

        if not to_delete:
            print("삭제할 데이터 없음")
            return

        ids = tuple(to_delete)

        # 2. 자식 테이블 먼저 삭제
        for table in ["user_profile", "user_condition_snapshots", "consents"]:
            r = await conn.execute(text(f"DELETE FROM {table} WHERE cognito_id = ANY(:ids)"), {"ids": list(ids)})
            print(f"{table} 삭제: {r.rowcount}행")

        # 3. supplements 테이블 삭제 (user_id가 cognito_id인 경우)
        for table in ["current_supplements", "intake_supplements"]:
            try:
                r = await conn.execute(text(f"DELETE FROM {table} WHERE cognito_id = ANY(:ids)"), {"ids": list(ids)})
                print(f"{table} 삭제: {r.rowcount}행")
            except Exception as e:
                print(f"{table} 스킵: {e}")

        # 4. users 삭제
        r = await conn.execute(text("DELETE FROM users WHERE cognito_id = ANY(:ids)"), {"ids": list(ids)})
        print(f"users 삭제: {r.rowcount}행")

asyncio.run(fix())
