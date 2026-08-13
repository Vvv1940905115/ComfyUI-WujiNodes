# -*- coding: utf-8 -*-
'''工坊提示词 · 后端 API 路由（工具栏：提示词优化 / 翻译）。'''

from aiohttp import web
from server import PromptServer

from .utils import llm_api


@PromptServer.instance.routes.post('/wuji/optimize_prompt')
async def wuji_optimize_prompt(request):
    try:
        data = await request.json()
        text = (data.get('text') or '').strip()
        if not text:
            return web.json_response({'success': False, 'error': 'empty'})
        result = llm_api.optimize_prompt(text)
        return web.json_response({'success': True, 'text': result})
    except Exception as e:  # noqa: BLE001
        return web.json_response({'success': False, 'error': str(e)})


@PromptServer.instance.routes.post('/wuji/translate')
async def wuji_translate(request):
    try:
        data = await request.json()
        text = (data.get('text') or '').strip()
        if not text:
            return web.json_response({'success': False, 'error': 'empty'})
        result = llm_api.smart_translate(text)
        return web.json_response({'success': True, 'text': result})
    except Exception as e:  # noqa: BLE001
        return web.json_response({'success': False, 'error': str(e)})

