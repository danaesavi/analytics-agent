.PHONY: preprocess run eval clean

preprocess:
	python data/preprocess_airbnb.py

run:
	python -m agent.run --data data/sample.parquet --question "Top 5 neighbourhoods by average price"

eval:
	python -m eval.run_eval --data data/sample.parquet

clean:
	rm -rf outputs/*