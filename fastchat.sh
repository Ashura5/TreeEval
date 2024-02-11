log_dir="your log_dir"

python3 -m fastchat.serve.controller --host localhost --port 23241 >$log_dir/controller.log 2>$log_dir/controller.err &

sleep 10
CUDA_VISIBLE_DEVICES=0 python3 -m fastchat.serve.multi_model_worker \
    --model-path ./LLMs/Xwin-LM-13B-V0.1 \
    --model-names Xwin-LM-13B-V0.1 \
    --model-path ./LLMs/Mistral-7B-Instruct-v0.2 \
    --model-names Mistral \
    --worker-address http://localhost:23251 \
    --controller-address http://localhost:23241 \
    --host localhost --port 23251 >$log_dir/1.log 2>$log_dir/1.err &

CUDA_VISIBLE_DEVICES=1 python3 -m fastchat.serve.multi_model_worker \
    --model-path ./LLMs/WizardLM-13B-V1.2 \
    --model-names WizardLM-13B-V1.2 \
    --model-path ./LLMs/zephyr-7b-beta \
    --model-names zephyr-7b-beta \
    --worker-address http://localhost:23252 \
    --controller-address http://localhost:23241 \
    --host localhost --port 23252 >$log_dir/2.log 2>$log_dir/2.err &

CUDA_VISIBLE_DEVICES=2 python3 -m fastchat.serve.model_worker \
    --model-path ./LLMs/vicuna-33b-v1.3 \
    --model-name vicuna-33b-v1.3 \
    --worker-address http://localhost:23353 \
    --controller-address http://localhost:23241 \
    --host localhost --port 23353 >$log_dir/3.log 2>$log_dir/3.err &

CUDA_VISIBLE_DEVICES=3 python3 -m fastchat.serve.model_worker \
    --model-path ./LLMs/bge-large-en-v1.5 \
    --model-name bge-large-en-v1.5 \
    --worker-address http://localhost:23253 \
    --controller-address http://localhost:23241 \
    --host localhost --port 23253 >$log_dir/4.log 2>$log_dir/4.err &

CUDA_VISIBLE_DEVICES=3 python3 -m fastchat.serve.model_worker \
    --model-path ./LLMs/Yi-34B-Chat  \
    --model-name Yi-34B-Chat \
    --worker-address http://localhost:23354 \
    --controller-address http://localhost:23241 \
    --host localhost --port 23354 >$log_dir/5.log 2>$log_dir/5.err &
# After the above command runs, run the following command
# python3 -m fastchat.serve.openai_api_server --host localhost --port 23261 --controller-address http://localhost:23241
