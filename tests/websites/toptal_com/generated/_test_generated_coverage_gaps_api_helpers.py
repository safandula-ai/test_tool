"""Helper functions for generated coverage tests."""

from __future__ import annotations

import json
from pathlib import Path


async def fetch_json_via_browser(
    page,
    *,
    path: str,
    method: str,
) -> dict[str, object]:
    return await page.evaluate(
        '''async ([path, method]) => {
            const response = await fetch(path, {
                method,
                credentials: "include",
                headers: { Accept: "application/json" },
            });
            const text = await response.text();
            return { status: response.status, text };
        }''',
        [path, method],
    )


def load_generated_case_data(
    module_file: str,
    file_name: str,
) -> dict[str, dict[str, object]]:
    data_path = Path(module_file).with_name(file_name)
    if not data_path.is_file():
        return {}
    return json.loads(data_path.read_text(encoding='utf-8'))
