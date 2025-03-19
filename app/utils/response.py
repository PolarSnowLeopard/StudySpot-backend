def success_response(data=None, message="success", code=200):
    """生成成功响应格式

    Args:
        data (Any, optional): 返回的数据. Defaults to None.
        message (str, optional): 成功信息. Defaults to "success".
        code (int, optional): 状态码. Defaults to 0.

    Returns:
        dict: 格式化的响应字典
    """
    response = {
        "code": code,
        "message": message
    }
    
    if data is not None:
        response["data"] = data

    return response
        

def error_response(message="error", code=400):
    """生成错误响应格式

    Args:
        message (str, optional): 错误信息. Defaults to "error".
        code (int, optional): 错误代码. Defaults to 1.

    Returns:
        dict: 格式化的响应字典
    """
    return {
        "code": code,
        "message": message
    } 