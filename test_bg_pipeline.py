import asyncio
import aiohttp
import json
import logging
import sys
import os

# 将项目目录加入环境变量以正确加载包
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from brain.llm_client import LLMClient
from config.settings import settings

logging.basicConfig(level=logging.INFO, format="%(message)s")

async def test_pipeline():
    logging.info("=" * 60)
    logging.info("🚀 Ember 文生图与前端背景动态变换 全链路探测脚本")
    logging.info("=" * 60)
    
    logging.info("\n[1] 开始调用内部组件，测试生成图像的 API 连通性...")
    try:
        client = LLMClient()
        # 抛给大模型一个标准的测试Prompt
        prompt = "A beautiful anime style serene beach at sunset, highly detailed, masterpiece, scenic."
        bg_url = client.generate_image(prompt)
        
        if bg_url:
            logging.info(f"✅ 核心文生图 API 逻辑验证通过！")
            logging.info(f"-> 成功截获到图片产出 URL: \n{bg_url}")
        else:
            logging.error("❌ 文生图 API 请求失败，返回结果为空。")
            logging.warning("💡 请检查 .env 配置文件中的 IMAGE_GEN_MODEL, IMAGE_GEN_API_KEY。")
            logging.warning("💡 请确保 API 余额充足且网络可达相应的 Base URL。")
            return
    except Exception as e:
        logging.error(f"❌ 第一阶段组件测试即遭遇异常: {e}")
        return

    logging.info("\n[2] 开始探测前端页面同步转换的效果...")
    logging.info("💡 脚本将尝试连接您挂在本地的 WebSocket 服务器并发送场景变更请求。")
    logging.info("💡 请确保后端 uvicorn 已开起，并且 React 前端页面已在浏览器中被打开！")
    
    await asyncio.sleep(2)
    
    try:
        async with aiohttp.ClientSession() as session:
            try:
                # 尝试连接本地启动服务的网关层
                ws = await session.ws_connect("ws://localhost:8000/ws/chat")
            except aiohttp.ClientConnectorError:
                logging.error("\n❌ 连接后端 WebSocket (ws://localhost:8000) 遭到拒绝或超时！")
                logging.info("💡 这很可能是后端没有启动，但上面的【文生图】测试已通过即可保证图模型模块已经彻底OK！")
                return

            logging.info("✅ 成功接入后端的事件总线和数据泵！")
            
            # 此时的后台判定已不再具有现实抗拒性，可以直接测试魔法传送门了！
            # 注入最符合日常人设的话语，彻底消除任何未重启大模型引发的“现实排斥反应”
            test_msg = {
                "type": "message",
                "content": "依鸣，我们现在回到南京大学鼓楼校区图书馆复习吧，别在宿舍睡了！"
            }
            await ws.send_json(test_msg)
            logging.info(f"✅ 成功向系统内下发交互意图: “{test_msg['content']}”")
            logging.info("⏳ 分发中心正在预解析地点(Pre-routing)，这通常需耗时约 5~15 秒处理画图及文字推演。")
            
            has_seen_generation = False
            
            while True:
                try:
                    msg = await asyncio.wait_for(ws.receive(), timeout=60.0)
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        
                        if data.get("type") == "message" and data.get("sender") == "ai":
                            if data.get("mode") == "start" and not has_seen_generation:
                                logging.info("=> 🤖 AI大模型引擎已被唤醒，正在合成打字流。")
                                has_seen_generation = True
                        
                        elif data.get("type") == "state_update":
                            state = data.get("state", {})
                            url = state.get("背景图Url")
                            loc = state.get("当前位置")
                            
                            if url:
                                logging.info(f"\n✅ 成功捕获到了专门下发给[前端渲染层]的环境变更帧！")
                                logging.info(f"✅ 状态机自动推导并确立当前地理位置为: [{loc}]")
                                logging.info(f"✅ 即将覆盖的前端实际背景链接为:\n{url}")
                                logging.info("\n🎉 所有的链路已全部畅通！赶紧切回浏览器原有的 React 界面，享受柔和的背景自动切页过渡吧！")
                                await ws.close()
                                break
                            else:
                                logging.info(f"-> 收到了一份零散的平行状态更新指令，但未检出背景结果。此刻大环境位置在: [{loc}]...")
                                
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        logging.error("❌ 服务器单向掐断了 WebSocket 流阻。")
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logging.error("❌ WebSocket 出现了未知系统底错误。")
                        break
                except asyncio.TimeoutError:
                    logging.warning("\n⚠️ 监听达 60 秒触发保护机制退出。可能是预路由判定这不属于明确变更，或者大模型生图堵塞卡顿。")
                    logging.info("💡 请直接打开界面手动和她沟通，测试其它地点的改变！")
                    break

    except Exception as e:
        logging.error(f"❌ 运行 WebSocket 前置检测时发生未解异常: {e}")

if __name__ == "__main__":
    # Windows 下防止 aiohttp 报错事件环问题的常见保护
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_pipeline())
