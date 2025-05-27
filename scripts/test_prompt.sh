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

optimize --prompt="prompt-5-en.md" -e --api_key="sk-wMRk3xvAGOkLhZ7WQhezrv9JYyukspkMjRLFWpLzDwxfiAhF" --base_url="https://yunwu.ai/v1" --model="gemini-2.5-flash-preview-05-20"