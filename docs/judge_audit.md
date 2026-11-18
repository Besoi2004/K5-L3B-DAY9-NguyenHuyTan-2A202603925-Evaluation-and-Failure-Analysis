# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`. Judge chạy replay (verdict có sẵn trong CSV), FAIL là lớp dương tính.

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Đạt (exit 0) | **dùng** (non-blocking, kèm sửa rubric) |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không đạt κ và R (exit 1) | **loại** |

Ma trận nhầm lẫn:

| | tp | fp | fn | tn | Tỉ lệ FAIL quan sát | Sau Rogan-Gladen |
|---|---|---|---|---|---|---|
| tone_ok | 24 | 4 | 6 | 66 | 0.28 | 0.30 |
| helpful | 9 | 0 | 21 | 70 | 0.09 | 0.30 |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 1 | tone H-008 "Em đã hoàn tiền cho anh rồi nha…" | PASS | FAIL | Người | Judge coi xưng "em… nha" là thân thiện. Rubric thêm: xưng hô phải là "LogiX" / "anh/chị", cấm "em", "bạn", "nha". |
| 2 | tone H-029 "Dạ, vui lòng chờ… không cần nhắn thêm." | PASS | FAIL | Người | Judge chỉ nhìn "Dạ, vui lòng". Rubric thêm: câu mệnh lệnh hoặc ngăn khách liên hệ là FAIL, kể cả khi mở đầu lịch sự. |
| 3 | tone H-051 "LogiX đã refund 90.000đ…" | FAIL | PASS | Người | Style guide CS của LogiX cho phép từ "refund". Rubric thêm danh sách thuật ngữ tiếng Anh được phép. |
| 4 | tone H-042 "Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ." | FAIL | PASS | Người | Judge phạt vì "thiếu xin lỗi". Rubric ghi rõ: không bắt buộc xin lỗi khi yêu cầu đã được giải quyết. |
| 5 | tone H-081 "Dạ, đơn O-107 chưa đủ điều kiện hoàn…" | FAIL | PASS | **Judge** | Người đọc nhầm ticket, judge đúng. Hành động: sửa nhãn người, không sửa rubric. Nhãn người cũng có lỗi, nên cần 2 người gán nhãn độc lập. |
| 6 | tone H-063 "…đã hoàn 20.000đ và sẽ hoàn thêm…" | PASS | FAIL | Người | Hứa hẹn ngoài kết quả hệ thống. Đây không hẳn là lỗi giọng văn mà là lời hứa sai, nên phải chấm bằng code (so với ledger), không giao cho judge tone. |
| 7 | helpful HL-015 "Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ." | PASS | FAIL | Người | Ledger ghi 40.000đ. Judge không thấy ledger, nên không thể bắt được lỗi số tiền (FM-08). Lỗi này phải giao cho grader code. |
| 8 | helpful HL-016 / HL-043 (xin lỗi dài, lặp lại, số tiền sai) | PASS | FAIL | Người | Judge thưởng cho câu dài và nhiều lời xin lỗi (verbosity bias), trong khi số tiền sai so với ledger. Rubric: xin lỗi lặp lại không cộng điểm. |
| 9 | helpful HL-047 "Ok bạn, đơn O-515 xử lý rồi nhé." | PASS | FAIL | Người | Không nói kết quả hay số tiền. Rubric thêm: reply phải nêu trạng thái và số tiền cụ thể. |

## Kết luận
- **Loại `helpful`.** Recall chỉ 0.30: judge bỏ sót 21/30 reply mà người gán FAIL (fn=21). κ=0.375 dưới sàn 0.6. Precision 1.0 chỉ cho biết khi judge nói FAIL thì đúng, nhưng judge hầu như không bao giờ nói FAIL (9/100). Dùng judge này làm gate thì 70% reply tệ vẫn được merge. Tỉ lệ FAIL quan sát được (0.09) thấp hơn hẳn tỉ lệ sau hiệu chỉnh Rogan-Gladen (0.30), nên con số từ judge sẽ làm agent trông tốt hơn thực tế gấp hơn 3 lần.
  Các case bị bỏ sót theo ba kiểu: (a) số tiền trong reply khác ledger, judge không có ledger nên không thể biết; (b) xin lỗi dài dòng được chấm cao; (c) trả lời mơ hồ, không có số tiền. Kiểu (a) chính là FM-08 và phải chấm bằng code (metric FM-08 ở M3), không bao giờ giao cho judge.
- **Dùng `tone_ok`.** κ=0.757, P=0.857, R=0.80, đều trên sàn. Rogan-Gladen điều chỉnh tỉ lệ FAIL quan sát 0.28 lên 0.30, chênh lệch nhỏ. Vẫn để non-blocking, vì giọng văn không ảnh hưởng tới tiền hay approval, và vẫn còn 6 fn / 4 fp ở các case 1–4 và 6. Sau khi sửa rubric như bảng trên, cần chấm lại trên nhãn mới.
- **Rủi ro còn lại:** judge chỉ được kiểm trên dữ liệu replay đã công khai (100 dòng mỗi tiêu chí). Cần thêm nhãn người mới để có tập held-out thật. Nhãn người cũng sai (case 5), nên cần ít nhất 2 người gán nhãn và đo độ đồng thuận giữa hai người.
