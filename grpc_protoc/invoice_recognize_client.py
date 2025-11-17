from configparser import ConfigParser
import inspect
from typing import Any, Optional, List
import grpc
from grpc_protoc.invoice_rpc_pb2_grpc import InvoiceRpcStub
from grpc_protoc import invoice_rpc_pb2

async def recognize_invoice(file_name: str):
    cp = ConfigParser()
    cp.read("cfg/beautify_report.cfg")
    rpc_host = cp.get("rpc", "host")
    rpc_port = cp.get("rpc", "port")
    rpc_url = f"{rpc_host}:{rpc_port}"
    channel = grpc.aio.insecure_channel(rpc_url)
    stub = InvoiceRpcStub(channel)
    request = invoice_rpc_pb2.InvoiceRecognizeReq(file_name=file_name, flag=1)
    try:
        call = stub.invoice_recognize(request)
        # 如果是 awaitable（unary），直接 await 并返回单个响应
        if inspect.isawaitable(call):
            resp = await call
            return resp
        # 否则把流式响应收集到列表并返回
        results: List[Any] = []
        async for item in call:
            results.append(item)
        if results:
            # 如果 results 中的第一项已经是 InvoiceRecognizeResp，直接返回
            if isinstance(results[0], invoice_rpc_pb2.InvoiceRecognizeResp):
                return results[0]
            resp = invoice_rpc_pb2.InvoiceRecognizeResp()
            resp.result = results[0].result
            resp.msg = results[0].msg
            resp.id = results[0].id
            return resp
        return None
    except grpc.RpcError as e:
        print(f"gRPC 调用失败: {e.code()} - {e.details()}")
        return None
    finally:
        await channel.close()


async def recognize_certificate(file_name: str):
    cp = ConfigParser()
    cp.read("cfg/beautify_report.cfg")
    rpc_host = cp.get("rpc", "host")
    rpc_port = cp.get("rpc", "port")
    rpc_url = f"{rpc_host}:{rpc_port}"
    channel = grpc.aio.insecure_channel(rpc_url)
    stub = InvoiceRpcStub(channel)
    request = invoice_rpc_pb2.InvoiceRecognizeReq(file_name=file_name, flag=1)
    try:
        call = stub.certificate_recognize(request)
        # 如果是 awaitable（unary），直接 await 并返回单个响应
        if inspect.isawaitable(call):
            resp = await call
            return resp
        # 否则把流式响应收集到列表并返回
        results: List[Any] = []
        async for item in call:
            results.append(item)
        if results:
            # 如果 results 中的第一项已经是 InvoiceRecognizeResp，直接返回
            if isinstance(results[0], invoice_rpc_pb2.InvoiceRecognizeResp):
                return results[0]
            resp = invoice_rpc_pb2.InvoiceRecognizeResp()
            resp.result = results[0].result
            resp.msg = results[0].msg
            resp.id = results[0].id
            return resp
        return None
    except grpc.RpcError as e:
        print(f"gRPC 调用失败: {e.code()} - {e.details()}")
        return None
    finally:
        await channel.close()        