# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi bạn 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `<shape> <claim>@<seed>`, run ID trong report |
| Triệu chứng | Grader nào fail; reply nói gì so với ledger ghi gì |
| Bước sai đầu tiên | Số thứ tự event + kind + trích payload (≤1 dòng) |
| Vì sao là bước *đầu tiên* | Các bước trước đó đúng ra sao (dẫn số event) |
| Failure mode | Mã FM-xx trong `docs/failure_taxonomy.md` |
| Đối chứng | Cùng claim@seed trên shape `fixed`: bước đó khác thế nào |
| Regression test | Tên test + grader/assert nào bắt được; đã thấy fail trên variant lỗi và pass trên `fixed` chưa |
| Chưa chắc chắn | Điều trace không chứng minh được |

## Case của tôi: `seeded_regression C-002@11`

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run ID `R-seeded_regression-C-002-s11` (item `E-002`, matrix T02) |
| Triệu chứng | Lab 8 grader FAIL: `status resolved != denied`. Ledger ghi `refund_vnd=20000`, `refund_count=1`, nhãn là 0 và 0. Reply "Dạ, LogiX đã hoàn 20.000đ cho đơn O-202." khớp ledger, nên đọc reply thì không thấy lỗi; phải đọc ledger. |
| Bước sai đầu tiên | Event 3 `model_override {"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event 1 `handoff` đúng contract (`check_applicable_policy`, chỉ tool read-only). Event 2 `investigator` đọc đúng DB: O-202 có `delay_days=2`. Event 3 thay số đó bằng "5 ngày" lấy từ ticket. Event 4 `quote` 20.000 (clause `SHIP-LATE-03`, cần ≥3 ngày) chỉ là hệ quả của số ngày sai. |
| Failure mode | FM-03 `ticket_trust` |
| Đối chứng | `fixed C-002@11`: không có event `model_override`; event 3 `quote {"amount_vnd": 0, "reason": "no_entitlement"}`, status `denied`, ledger 0. Lab 8 grader PASS. |
| Regression test | `src/tests/test_lab9_trace_case.py::test_c002_ticket_trust`: assert có `model_override`, ledger 20.000 và lab8 FAIL trên `seeded_regression`; không có `model_override`, ledger 0 và lab8 PASS trên `fixed`. Đã chạy: 2 passed. Trong eval, grader `DbFactKept` (metric `db_fact_kept`) và `pass_rate` bắt được lỗi này. |
| Chưa chắc chắn | Trace chỉ cho thấy agent đã tin ticket, không cho thấy *vì sao* (MockLLM không có lập luận). Swarm gốc chỉ dính lỗi này ở seed 55 (`seed % 5 == 0`); với LLM thật, tần suất có thể khác. Biến thể `quiet_override` cùng lỗi nhưng không ghi event, nên `DbFactKept` sẽ không bắt được; chỉ ledger vs nhãn bắt được. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
