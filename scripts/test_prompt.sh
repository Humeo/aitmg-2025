##

# shellcheck disable=SC1073
case "$1" in
  home)
    echo '执行 python bin/opt_prompt.py --model="qwen3:8b" --api_key="" --base_url=""'
    python bin/opt_prompt.py optimize --model="qwen3:8b" --api_key="" --base_url=""
    ;;
  qwen3-8b)
    echo '执行 python bin/opt_prompt.py --model="qwen3:8b" --api_key="" --base_url="" --only_evaluate=True'
    python bin/opt_prompt.py --model="qwen3:8b" --api_key="" --base_url="" --only_evaluate=True
    ;;
  qwen3:8b)
    echo '执行 python bin/opt_prompt.py --model="qwen3:8b" --api_key="" --base_url="" --only_evaluate=True'
    python bin/opt_prompt.py --model="qwen3:8b" --api_key="" --base_url="" --only_evaluate=True
    ;;
  qwen3-32b)
  echo '执行 python bin/opt_prompt.py --model="qwen3:8b" --api_key="" --base_url="" --only_evaluate=True'
  python bin/opt_prompt.py --model="qwen3:8b" --api_key="" --base_url="" --only_evaluate=True
  ;;
  *)
    echo "not support model: $2"
  ;;
esac