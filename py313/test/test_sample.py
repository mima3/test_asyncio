import asyncio
import pytest
from unittest.mock import patch, AsyncMock
from file.test_file import read_file


class TestAsync:
    def test_sample(self):
        assert True

    @pytest.mark.asyncio
    async def test_async(self):
        await asyncio.sleep(0)
        assert True

    @pytest.mark.asyncio
    async def test_async_read_file(self):
        contents = await read_file("../docker/ssh/downloads/0001.md")
        print(contents)
        assert contents.split("\n")[0] == "仏説摩訶般若波羅蜜多心経"

    @pytest.mark.asyncio
    async def test_async_read_file_mock(self):
        file_obj = AsyncMock()
        file_obj.read.return_value = "hello"
        cm = AsyncMock()
        cm.__aenter__.return_value = file_obj
        cm.__aexit__.return_value = None
        with patch("file.test_file.aiofiles.open", return_value=cm) as m_open:
            print(m_open)
            contents = await read_file("../docker/ssh/downloads/0001.md")
            print(contents)
            assert contents.split("\n")[0] == "hello"
