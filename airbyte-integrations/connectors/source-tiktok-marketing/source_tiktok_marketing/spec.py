#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from typing import Optional

from pydantic import BaseModel, Field


class SourceTikTokMarketingSpec(BaseModel):
    class Config:
        title = "TikTok Marketing Source Spec"

    access_token: str = Field(
        description="Long-term Authorized Access Token.",
        airbyte_secret=True
    )
    is_sandbox: Optional[bool] = Field(
            default=False,
            description="Defines whether use the SANDBOX or PRODUCTION environment. Defines whether use the SANDBOX or PRODUCTION environment.",
    )
    start_date: str = Field(
        description="Start Date in format: YYYY-MM-DD.",
        default="1970-01-01",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    )
