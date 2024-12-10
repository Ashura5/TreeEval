# Introduction #
This is the code repository corresponding to the paper "TreeEval: Benchmark-Free Evaluation of Large Language Models through Tree Planning"

Our work has been accepted by AAAI2025, and everyone is welcome to follow up.

here is an overview of our method
![图片说明](.//images//method.png) 

TreeEval naturally avoids the problem of test data leakage by discarding the fixed test set.

# Install #
Refer to the installation of [FastChat](https://github.com/lm-sys/FastChat)

The model we use can be found in huggingface:
[Yi-34B-Chat](https://huggingface.co/01-ai/Yi-34B-Chat)
[Xwin-LM-13B-V0.1](https://huggingface.co/Xwin-LM/Xwin-LM-13B-V0.1)
[vicuna-33b-v1.3](https://huggingface.co/lmsys/vicuna-33b-v1.3)
[Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
[WizardLM-13B-V1.2](https://huggingface.co/WizardLM/WizardLM-13B-V1.2)
# Run steps #
1. start the server of fastchat
	1. Modify log_dir in fastchat.sh
	1. `bash fastchat.sh`
	2. `python3 -m fastchat.serve.openai_api_server --host localhost --port 23261 --controller-address http://localhost:23241`
2. Configure the config.yaml file, copy the config.yaml file, and modify it to config_modelname.yaml
3. `python main.py`

# Citation #
if you find this useful for your work, please cite:
<pre>
@article{li2024treeeval,
      title={TreeEval: Benchmark-Free Evaluation of Large Language Models through Tree Planning}, 
      author={Xiang Li and Yunshi Lan and Chao Yang},
      year={2024},
      eprint={2402.13125},
      archivePrefix={arXiv},
      journal={arXiv preprint arXiv:2402.13125},
      primaryClass={cs.CL}
}
</pre>