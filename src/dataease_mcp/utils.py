import base64
import threading
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


def aes_decrypt(encrypted_data: str, key: str, iv: str = "0000000000000000") -> str:
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    encrypted_bytes = base64.b64decode(encrypted_data)
    decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    return decrypted.decode("utf-8")


def rsa_encrypt(data: str, public_key_pem: str) -> str:
    padding_needed = 4 - len(public_key_pem) % 4
    if padding_needed != 4:
        public_key_pem += "=" * padding_needed
    der = base64.b64decode(public_key_pem)
    public_key = serialization.load_der_public_key(der)

    data_bytes = data.encode("utf-8")
    max_block = 245
    result = bytearray()
    for i in range(0, len(data_bytes), max_block):
        block = data_bytes[i : i + max_block]
        encrypted = public_key.encrypt(block, padding.PKCS1v15())
        result.extend(encrypted)
    return base64.b64encode(bytes(result)).decode("utf-8")


def parse_dekey(dekey_response: str) -> str:
    separator_marker = "-pk_separator-"
    separator_b64 = base64.urlsafe_b64encode(
        separator_marker.encode("utf-8")
    ).decode("utf-8")
    if separator_b64 not in dekey_response:
        raise ValueError(
            f"Cannot find separator '{separator_b64}' in dekey response"
        )
    parts = dekey_response.split(separator_b64, 1)
    if len(parts) != 2:
        raise ValueError("Invalid dekey response format")
    encrypted_pk = parts[0]
    aes_key = parts[1]
    return aes_decrypt(encrypted_pk, aes_key)


def generate_view_id() -> int:
    return SnowflakeIdGenerator.instance().next_id()


def safe_int(value):
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value.strip())
    return int(value)


CHART_TYPE_LIST = [
    "table-info",
    "table-normal",
    "table-pivot",
    "t-heatmap",
    "bar",
    "bar-horizontal",
    "bar-group",
    "bar-group-stack",
    "bar-stack",
    "bar-stack-horizontal",
    "percentage-bar-stack",
    "percentage-bar-stack-horizontal",
    "bar-range",
    "progress-bar",
    "bullet-graph",
    "bidirectional-bar",
    "line",
    "area",
    "area-stack",
    "chart-mix",
    "chart-mix-stack",
    "chart-mix-group",
    "chart-mix-dual-line",
    "pie",
    "pie-rose",
    "pie-donut",
    "pie-donut-rose",
    "scatter",
    "quadrant",
    "multi-scatter",
    "radar",
    "funnel",
    "word-cloud",
    "waterfall",
    "treemap",
    "sankey",
    "circle-packing",
    "indicator",
    "gauge",
    "liquid",
    "map",
    "flow-map",
    "symbolic-map",
    "heat-map",
    "bubble-map",
    "rich-text",
]

_CHART_TYPE_DESCRIPTIONS = {
    "table-info": "明细表",
    "table-normal": "汇总表",
    "table-pivot": "透视表",
    "t-heatmap": "表格热力图",
    "bar": "柱状图",
    "bar-horizontal": "横向柱状图",
    "bar-group": "分组柱状图",
    "bar-group-stack": "分组堆叠柱状图",
    "bar-stack": "堆叠柱状图",
    "bar-stack-horizontal": "横向堆叠柱状图",
    "percentage-bar-stack": "百分比堆叠柱状图",
    "percentage-bar-stack-horizontal": "横向百分比堆叠柱状图",
    "bar-range": "区间条形图",
    "progress-bar": "进度条",
    "bullet-graph": "子弹图",
    "bidirectional-bar": "双向条形图",
    "line": "折线图",
    "area": "面积图",
    "area-stack": "堆叠面积图",
    "chart-mix": "组合图",
    "chart-mix-stack": "堆叠组合图",
    "chart-mix-group": "分组组合图",
    "chart-mix-dual-line": "双线组合图",
    "pie": "饼图",
    "pie-rose": "玫瑰图",
    "pie-donut": "环形图",
    "pie-donut-rose": "环形玫瑰图",
    "scatter": "散点图",
    "quadrant": "象限图",
    "multi-scatter": "多维散点图",
    "radar": "雷达图",
    "funnel": "漏斗图",
    "word-cloud": "词云图",
    "waterfall": "瀑布图",
    "treemap": "矩形树图",
    "sankey": "桑基图",
    "circle-packing": "圆形打包图",
    "indicator": "指标卡",
    "gauge": "仪表盘",
    "liquid": "水球图",
    "map": "地图",
    "flow-map": "流向地图",
    "symbolic-map": "符号地图",
    "heat-map": "热力地图",
    "bubble-map": "气泡地图",
    "rich-text": "富文本",
}


class SnowflakeIdGenerator:
    _instance = None
    _lock = threading.Lock()
    _sequence = 0
    _last_timestamp = -1
    _epoch = 1480166465631
    _datacenter_id = 1
    _worker_id = 1
    _datacenter_bits = 5
    _worker_bits = 5
    _sequence_bits = 12
    _max_sequence = (1 << _sequence_bits) - 1
    _timestamp_left_shift = _datacenter_bits + _worker_bits + _sequence_bits
    _datacenter_left_shift = _worker_bits + _sequence_bits
    _worker_left_shift = _sequence_bits

    def __init__(self):
        pass

    @classmethod
    def instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def next_id(self) -> int:
        with self._lock:
            timestamp = int(time.time() * 1000)
            if timestamp < self._last_timestamp:
                timestamp = self._last_timestamp
            if timestamp == self._last_timestamp:
                self._sequence = (self._sequence + 1) & self._max_sequence
                if self._sequence == 0:
                    while timestamp <= self._last_timestamp:
                        time.sleep(0.001)
                        timestamp = int(time.time() * 1000)
            else:
                self._sequence = 0
            self._last_timestamp = timestamp
            return (
                ((timestamp - self._epoch) << self._timestamp_left_shift)
                | (self._datacenter_id << self._datacenter_left_shift)
                | (self._worker_id << self._worker_left_shift)
                | self._sequence
            )
