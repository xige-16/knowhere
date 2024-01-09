import knowhere
import json
import pytest
import numpy as np
from bfloat16 import bfloat16

test_data = [
    (
        "FLAT",
        {
            "dim": 256,
            "k": 15,
            "metric_type": "L2",
        },
    ),
    (
        "IVFFLAT",
        {
            "dim": 256,
            "k": 15,
            "metric_type": "L2",
            "nlist": 1024,
            "nprobe": 1024,
        },
    ),
    (
        "IVFFLATCC",
        {
            "dim": 256,
            "k": 15,
            "metric_type": "L2",
            "nlist": 1024,
            "nprobe": 1024,
            "ssize" : 48
        },
    ),
    (
        "IVFSQ",
        {
            "dim": 256,
            "k": 15,
            "metric_type": "L2",
            "nlist": 1024,
            "nprobe": 1024,
        },
    ),
    (
        "SCANN",
        {
            "dim": 256,
            "k": 15,
            "metric_type": "L2",
            "m": 128,
            "nbits": 4,
            "nlist": 1024,
            "nprobe": 1024,
            "reorder_k": 1500,
            "with_raw_data": True,
        },
    ),
]


@pytest.mark.parametrize("name,config", test_data)
def test_index(gen_data, faiss_ans, recall, error, name, config):
    print(name, config)
    version = knowhere.GetCurrentVersion()
    idx = knowhere.CreateIndex(name, version)
    xb, xq = gen_data(10000, 100, 256)

    idx.Build(
        knowhere.ArrayToDataSet(xb),
        json.dumps(config),
    )

    ans, _ = idx.Search(
        knowhere.ArrayToDataSet(xq),
        json.dumps(config),
        knowhere.GetNullBitSetView()
    )
    k_dis, k_ids = knowhere.DataSetToArray(ans)
    f_dis, f_ids = faiss_ans(xb, xq, config["metric_type"], config["k"])
    if (name != "IVFSQ"):
        assert recall(f_ids, k_ids) >= 0.99
    else:
        assert recall(f_ids, k_ids) >= 0.70
    assert error(f_dis, f_dis) <= 0.01

    bitset = knowhere.CreateBitSet(xb.shape[0])
    for id in k_ids[:10,:1].ravel():
        bitset.SetBit(int(id))
    ans, _ = idx.Search(
        knowhere.ArrayToDataSet(xq),
        json.dumps(config),
        bitset.GetBitSetView()
    )

    k_dis, k_ids = knowhere.DataSetToArray(ans)
    if (name != "IVFSQ"):
        assert recall(f_ids, k_ids) >= 0.7
    else:
        assert recall(f_ids, k_ids) >= 0.5
    assert error(f_dis, f_dis) <= 0.01

@pytest.mark.parametrize("name,config", test_data)
def test_float16_index(gen_data_with_type, faiss_ans, recall, error, name, config):
    print(name, config)
    version = knowhere.GetCurrentVersion()
    idx = knowhere.CreateIndex(name, version, np.float16)
    xb, xq = gen_data_with_type(10000, 100, 256, np.float16)

    idx.Build(
        knowhere.ArrayToDataSet(xb),
        json.dumps(config),
    )

    ans, _ = idx.Search(
        knowhere.ArrayToDataSet(xq),
        json.dumps(config),
        knowhere.GetNullBitSetView()
    )
    k_dis, k_ids = knowhere.DataSetToArray(ans)
    f_dis, f_ids = faiss_ans(xb, xq, config["metric_type"], config["k"])
    if (name != "IVFSQ"):
        assert recall(f_ids, k_ids) >= 0.99
    else:
        assert recall(f_ids, k_ids) >= 0.70
    assert error(f_dis, f_dis) <= 0.01

    bitset = knowhere.CreateBitSet(xb.shape[0])
    for id in k_ids[:10,:1].ravel():
        if id < 0:
            continue
        bitset.SetBit(int(id))
    ans, _ = idx.Search(
        knowhere.ArrayToDataSet(xq),
        json.dumps(config),
        bitset.GetBitSetView()
    )

    k_dis, k_ids = knowhere.DataSetToArray(ans)
    if (name != "IVFSQ"):
        assert recall(f_ids, k_ids) >= 0.7
    else:
        assert recall(f_ids, k_ids) >= 0.5
    assert error(f_dis, f_dis) <= 0.01

@pytest.mark.parametrize("name,config", test_data)
def test_bfloat16_index(gen_data_with_type, faiss_ans, recall, error, name, config):
    print(name, config)
    version = knowhere.GetCurrentVersion()
    idx = knowhere.CreateIndex(name, version, bfloat16)
    xb, xq = gen_data_with_type(10000, 100, 256, bfloat16)

    idx.Build(
        knowhere.ArrayToDataSet(xb),
        json.dumps(config),
    )

    ans, _ = idx.Search(
        knowhere.ArrayToDataSet(xq),
        json.dumps(config),
        knowhere.GetNullBitSetView()
    )
    k_dis, k_ids = knowhere.DataSetToArray(ans)
    f_dis, f_ids = faiss_ans(xb, xq, config["metric_type"], config["k"])
    if (name != "IVFSQ"):
        assert recall(f_ids, k_ids) >= 0.99
    else:
        assert recall(f_ids, k_ids) >= 0.70
    assert error(f_dis, f_dis) <= 0.01

    bitset = knowhere.CreateBitSet(xb.shape[0])
    for id in k_ids[:10,:1].ravel():
        if id < 0:
            continue
        bitset.SetBit(int(id))
    ans, _ = idx.Search(
        knowhere.ArrayToDataSet(xq),
        json.dumps(config),
        bitset.GetBitSetView()
    )

    k_dis, k_ids = knowhere.DataSetToArray(ans)
    if (name != "IVFSQ"):
        assert recall(f_ids, k_ids) >= 0.7
    else:
        assert recall(f_ids, k_ids) >= 0.5
    assert error(f_dis, f_dis) <= 0.01
