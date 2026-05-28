import tiktoken


def count_tokens(text: str):

    encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))