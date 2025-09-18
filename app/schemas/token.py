from pydantic import BaseModel, Field

class Token(BaseModel):
    """JWT access token response model"""

    access_token: str = Field(
        description="Bearer token for API authentication",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(default="bearer", description="Token authentication scheme")
    expires_in: int = Field(
        description="Token expiration in seconds",
        examples=[1800],  # 30 minutes
    )


class TokenPayload(BaseModel):
    """Internal JWT payload structure (not exposed in API)"""

    sub: str = Field(
        description="Subject (user identifier)", examples=["user@example.com"]
    )
    exp: int = Field(
        description="Expiration timestamp (Unix epoch)", examples=[1717020800]
    )
    iat: int = Field(
        description="Issued at timestamp (Unix epoch)", examples=[1717019000]
    )


class TokenData(BaseModel):
    """Validated token data for dependency injection"""

    username: str = Field(
        description="User's unique email identifier", examples=["user@example.com"]
    )

    @classmethod
    def from_payload(cls, payload: TokenPayload) -> "TokenData":
        """Convert raw payload to validated token data"""
        return cls(username=payload.sub)
