import yaml

def load_config(path='config.yaml'):
    """加载并返回YAML配置文件内容"""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)