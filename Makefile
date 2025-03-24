default: all

GUIDS = $(shell cat ./data/guids.json | sed 's/\/\/.*$$//g' | jq -r '.[].guid' | sort | uniq)

all: zero_shot_responses \
	embeddings \
	zero_shot_dist_report zero_shot_class_report \
	image_embeddings cot_precompute \
	medprompt_responses \
	medprompt_dist_report medprompt_class_report 

IMAGE_EMBEDDINGS = $(foreach guid,$(GUIDS),./results/image-embeddings/$(guid).json)
image_embeddings: $(IMAGE_EMBEDDINGS)
./results/image-embeddings/%.json: ./data/pics/%.png
	mkdir -p ./results/image-embeddings/
	python ./scripts/image_embeddings.py --guid $* --out $@

cot_precompute: ./results/cot_data.json
./results/cot_data.json: $(IMAGE_EMBEDDINGS) $(RESPONSE_FILES)
	mkdir -p ./results/
	python scripts/precompute_cots.py --guids data/guids.json --out $@

MEDPROMPT_FILES = $(foreach guid,$(GUIDS),./results/medprompt-responses/$(guid).json)
medprompt_responses: $(MEDPROMPT_FILES) ./results/cot_data.json
./results/medprompt-responses/%.json: ./data/data/%.json ./data/pics/%.png ./data/guids.json ./results/cot_data.json
	mkdir -p ./results/medprompt-responses/
	python ./scripts/generate_medprompt_response.py --guid $* --model ${MODEL} --out $@ --guids data/guids.json --cotdata ./results/cot_data.json

RESPONSE_FILES = $(foreach guid,$(GUIDS),./results/zero-shot-responses/$(guid).json)
zero_shot_responses: $(RESPONSE_FILES)
./results/zero-shot-responses/%.json: ./data/data/%.json ./data/pics/%.png
	mkdir -p ./results/zero-shot-responses/
	python ./scripts/generate_response.py --guid $* --model ${MODEL} --out $@


ZERO_SHOT_RESPONSE_EMBEDDING_FILES = $(foreach guid,$(GUIDS),./results/zero-shot-responses-embeddings/$(guid).json)
zero_shot_response_embeddings: $(ZERO_SHOT_RESPONSE_EMBEDDING_FILES)
./results/zero-shot-responses-embeddings/%.json: ./results/zero-shot-responses/%.json
	mkdir -p ./results/zero-shot-responses-embeddings/
	python ./scripts/create_embeddings.py --input $< --out $@

MEDPROMPT_RESPONSE_EMBEDDING_FILES = $(foreach guid,$(GUIDS),./results/medprompt-responses-embeddings/$(guid).json)
medprompt_response_embeddings: $(MEDPROMPT_RESPONSE_EMBEDDING_FILES)
./results/medprompt-responses-embeddings/%.json: ./results/medprompt-responses/%.json
	mkdir -p ./results/medprompt-responses-embeddings/
	python ./scripts/create_embeddings.py --input $< --out $@

DATA_EMBEDDING_FILES = $(foreach guid,$(GUIDS),./results/data-embeddings/$(guid).json)
data_embeddings: $(DATA_EMBEDDING_FILES)
./results/data-embeddings/%.json: ./data/data/%.json
	mkdir -p ./results/data-embeddings/
	python ./scripts/create_embeddings.py --input $< --out $@

embeddings: zero_shot_response_embeddings medprompt_response_embeddings data_embeddings


ZERO_SHOT_RESPONSE_SELFCHECKGPT_FILES = $(foreach guid,$(GUIDS),./results/zero-shot-responses-selfcheckgpt/$(guid).json)
zero_shot_responses_selfcheckgpt: $(ZERO_SHOT_RESPONSE_SELFCHECKGPT_FILES)
./results/zero-shot-responses-selfcheckgpt/%.json: ./results/zero-shot-responses/%.json
	mkdir -p ./results/zero-shot-responses-selfcheckgpt/
	python ./scripts/perform_selfcheckgpt.py --input $< --out $@ --guid $*

MEDPROMPT_RESPONSE_SELFCHECKGPT_FILES = $(foreach guid,$(GUIDS),./results/medprompt-responses-selfcheckgpt/$(guid).json)
medprompt_responses_selfcheckgpt: $(MEDPROMPT_RESPONSE_SELFCHECKGPT_FILES)
./results/medprompt-responses-selfcheckgpt/%.json: ./results/medprompt-responses/%.json
	mkdir -p ./results/medprompt-responses-selfcheckgpt/
	python ./scripts/perform_selfcheckgpt.py --input $< --out $@ --guid $*

selfcheckgpt: zero_shot_responses_selfcheckgpt medprompt_responses_selfcheckgpt

DATA_FILES = $(foreach guid,$(GUIDS),./data/data/$(guid).json)
zero_shot_class_report: ./results/zero-shot-class-report.xlsx
./results/zero-shot-class-report.xlsx: $(RESPONSE_FILES) $(DATA_FILES) ./data/guids.json
	mkdir -p ./results
	python ./scripts/test_classification.py --guids ./data/guids.json --truth ./data/data --pred ./results/zero-shot-responses -o $@

zero_shot_dist_report: ./results/zero-shot-dist-report.xlsx
./results/zero-shot-dist-report.xlsx: $(DATA_EMBEDDING_FILES) $(ZERO_SHOT_RESPONSE_EMBEDDING_FILES) ./data/guids.json
	mkdir -p ./results
	python ./scripts/test_distances.py --guids ./data/guids.json --truth ./results/data-embeddings/ --pred ./results/zero-shot-responses-embeddings/ --out $@

zero_shot_selfcheckgpt_report: ./results/zero-shot-selfcheckgpt-report.xlsx
./results/zero-shot-selfcheckgpt-report.xlsx: $(ZERO_SHOT_RESPONSE_SELFCHECKGPT_FILES) ./data/guids.json
	mkdir -p ./results
	python ./scripts/test_selfcheckgpt.py --guids ./data/guids.json --scores ./results/zero-shot-responses-selfcheckgpt/ --out $@

medprompt_class_report: ./results/medprompt-class-report.xlsx
./results/medprompt-class-report.xlsx: $(MEDPROMPT_FILES) $(DATA_FILES) ./data/guids.json
	mkdir -p ./results
	python ./scripts/test_classification.py --guids ./data/guids.json --truth ./data/data --pred ./results/medprompt-responses -o $@

medprompt_dist_report: ./results/medprompt-dist-report.xlsx
./results/medprompt-dist-report.xlsx: $(DATA_EMBEDDING_FILES) $(MEDPROMPT_RESPONSE_EMBEDDING_FILES) ./data/guids.json
	mkdir -p ./results
	python ./scripts/test_distances.py --guids ./data/guids.json --truth ./results/data-embeddings/ --pred ./results/medprompt-responses-embeddings/ --out $@

medprompt_selfcheckgpt_report: ./results/medprompt-selfcheckgpt-report.xlsx
./results/medprompt-selfcheckgpt-report.xlsx: $(MEDPROMPT_RESPONSE_SELFCHECKGPT_FILES) ./data/guids.json
	mkdir -p ./results
	python ./scripts/test_selfcheckgpt.py --guids ./data/guids.json --scores ./results/medprompt-responses-selfcheckgpt/ --out $@
