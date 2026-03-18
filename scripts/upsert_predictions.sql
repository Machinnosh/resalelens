INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('260f8974-f04e-4c8b-b971-883667ca9a0e', 88, 1.2702, 1.2098, 1.0888, 0, 'high', 22, '{"6m": 1.27, "1y": 1.21, "2y": 1.149, "3y": 1.089}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('14096df7-9c17-4978-8215-b469e30b1f67', 86, 1.2091, 1.1515, 1.0364, 0, 'medium', 13, '{"6m": 1.209, "1y": 1.152, "2y": 1.094, "3y": 1.036}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('56fe7fc3-5fc0-48c5-8c58-9d601209315a', 62, 0.8666, 0.8253, 0.7428, 317000, 'medium', 15, '{"6m": 0.867, "1y": 0.825, "2y": 0.784, "3y": 0.743}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('508500e1-04fb-4c3e-8083-1b18d353dee5', 2, 0.041, 0.0391, 0.0352, 1215560, 'low', 3, '{"6m": 0.041, "1y": 0.039, "2y": 0.037, "3y": 0.035}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('a758c0c1-09b4-4376-8c7b-496087a19372', 81, 1.0769, 1.0256, 0.9231, 0, 'medium', 5, '{"6m": 1.077, "1y": 1.026, "2y": 0.974, "3y": 0.923}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('1feac66f-488c-4471-abcd-18aa3379046f', 100, 1.6234, 1.5461, 1.3915, 0, 'low', 1, '{"6m": 1.623, "1y": 1.546, "2y": 1.469, "3y": 1.391}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('0401740a-e19f-433c-a371-7fa0343d99c3', 65, 0.8925, 0.85, 0.765, 42000, 'low', 1, '{"6m": 0.892, "1y": 0.85, "2y": 0.807, "3y": 0.765}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('06bbb5e3-5862-4944-a450-fa914889e671', 57, 0.8128, 0.7741, 0.6967, 61000, 'low', 2, '{"6m": 0.813, "1y": 0.774, "2y": 0.735, "3y": 0.697}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('9f35de8f-0ee7-4472-8dc6-b55fefbf7eed', 10, 0.1826, 0.1739, 0.1565, 743500, 'high', 118, '{"6m": 0.183, "1y": 0.174, "2y": 0.165, "3y": 0.157}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('c128f1f0-8825-4d49-8af3-f79f6bf011ae', 7, 0.1258, 0.1198, 0.1078, 1034200, 'high', 26, '{"6m": 0.126, "1y": 0.12, "2y": 0.114, "3y": 0.108}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('b5e003bb-75ad-48f5-a80a-d9a9341134df', 4, 0.0724, 0.069, 0.0621, 1215001, 'low', 1, '{"6m": 0.072, "1y": 0.069, "2y": 0.066, "3y": 0.062}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('1c6ced48-c5ec-4a00-b4a2-1b90e60ffc3a', 51, 0.7514, 0.7156, 0.644, 213300, 'low', 3, '{"6m": 0.751, "1y": 0.716, "2y": 0.68, "3y": 0.644}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('806ea0d0-eb87-4051-870f-31aa49f8e3e7', 18, 0.3072, 0.2926, 0.2633, 141485, 'low', 2, '{"6m": 0.307, "1y": 0.293, "2y": 0.278, "3y": 0.263}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('bc88e194-5ea6-4455-b650-2557cc1a7c9f', 41, 0.622, 0.5924, 0.5332, 93750, 'high', 60, '{"6m": 0.622, "1y": 0.592, "2y": 0.563, "3y": 0.533}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('b37e2e77-b1c6-4516-b971-a7e467a18d6a', 38, 0.585, 0.5571, 0.5014, 115150, 'high', 82, '{"6m": 0.585, "1y": 0.557, "2y": 0.529, "3y": 0.501}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('d431133e-0de7-40c4-a98f-fc4312595a19', 49, 0.7324, 0.6975, 0.6277, 84702, 'low', 4, '{"6m": 0.732, "1y": 0.697, "2y": 0.663, "3y": 0.628}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('f6d5b1d8-0918-486a-80cb-1c80d62a8078', 2, 0.0456, 0.0434, 0.0391, 1224445, 'high', 145, '{"6m": 0.046, "1y": 0.043, "2y": 0.041, "3y": 0.039}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('cdb652fe-b0e0-4a7f-8032-fd2c7ff33aea', 2, 0.0415, 0.0395, 0.0356, 2065000, 'high', 95, '{"6m": 0.042, "1y": 0.04, "2y": 0.038, "3y": 0.036}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('8f4a9d27-5525-462f-975a-cd696a953702', 44, 0.6632, 0.6316, 0.5684, 350000, 'high', 75, '{"6m": 0.663, "1y": 0.632, "2y": 0.6, "3y": 0.568}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('70ec936a-25d1-4fa7-8742-d6d7a773eb4a', 70, 0.9528, 0.9074, 0.8167, 125000, 'high', 24, '{"6m": 0.953, "1y": 0.907, "2y": 0.862, "3y": 0.817}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('113ee069-cb59-4856-98f6-09c19c057314', 84, 1.1605, 1.1053, 0.9947, 0, 'medium', 7, '{"6m": 1.161, "1y": 1.105, "2y": 1.05, "3y": 0.995}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('2214bbe0-477b-45a4-8ab9-31c109aaa2d1', 7, 0.1247, 0.1187, 0.1069, 775500, 'high', 136, '{"6m": 0.125, "1y": 0.119, "2y": 0.113, "3y": 0.107}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('9fa47a84-cc6a-4cdb-af93-8f0bed2c1517', 23, 0.399, 0.38, 0.342, 465000, 'medium', 8, '{"6m": 0.399, "1y": 0.38, "2y": 0.361, "3y": 0.342}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('535eca91-ae89-432b-9798-481c88319620', 23, 0.3877, 0.3692, 0.3323, 410000, 'low', 1, '{"6m": 0.388, "1y": 0.369, "2y": 0.351, "3y": 0.332}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('4b1dc22c-c06a-4d93-9d45-50b37af2acec', 34, 0.5343, 0.5089, 0.458, 220999, 'high', 44, '{"6m": 0.534, "1y": 0.509, "2y": 0.483, "3y": 0.458}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('eecf687a-3afe-4808-b877-dfa46759c685', 1, 0.033, 0.0315, 0.0283, 271189, 'high', 49, '{"6m": 0.033, "1y": 0.031, "2y": 0.03, "3y": 0.028}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('3ae55f33-9120-4249-b070-de94ab16a573', 39, 0.6, 0.5714, 0.5143, 150000, 'low', 1, '{"6m": 0.6, "1y": 0.571, "2y": 0.543, "3y": 0.514}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('71a9b302-1a9d-4b79-ac31-c55eda7aca36', 11, 0.1931, 0.1839, 0.1655, 310110, 'high', 50, '{"6m": 0.193, "1y": 0.184, "2y": 0.175, "3y": 0.166}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();
INSERT INTO resale_predictions (product_id, resale_score, prr_6month, prr_1year, prr_3year, actual_cost_1year, confidence, transaction_count, decay_curve, model_version)
VALUES ('377dc519-cc43-4776-94ed-4747f26871a9', 18, 0.3115, 0.2966, 0.267, 56270, 'high', 50, '{"6m": 0.311, "1y": 0.297, "2y": 0.282, "3y": 0.267}'::jsonb, 'simple-prr-v1')
ON CONFLICT (product_id) DO UPDATE SET
resale_score=EXCLUDED.resale_score, prr_6month=EXCLUDED.prr_6month, prr_1year=EXCLUDED.prr_1year, prr_3year=EXCLUDED.prr_3year,
actual_cost_1year=EXCLUDED.actual_cost_1year, confidence=EXCLUDED.confidence, transaction_count=EXCLUDED.transaction_count,
decay_curve=EXCLUDED.decay_curve, model_version=EXCLUDED.model_version, updated_at=now();