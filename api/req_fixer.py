import subprocess
import sys
import re


FILE_PATH = "requirements.txt"
LATEST_SWITCH = "--latest"


def get_arg(index, raise_error=False):
  try:
    return sys.argv[index].lower()
  except:
    if raise_error:
      usage = f"usage: {sys.argv[0]} <package_name> [<version>] [--latest]"
      example = f"example: {sys.argv[0]} django --latest"
      raise SystemExit(f"{usage}\n{example}")
    return ""


def generate_package_str(package_name, version):
  if version:
    version = f"=={version}"

  return f"{package_name}{version}"


def get_package_info(package_name, version, install_latest):
  if install_latest:
    result = subprocess.run(["yolk", "-V", package_name], capture_output=True, text=True)
    version = result.stdout.replace("\r\n", "").split(" ")[1]

  return generate_package_str(package_name, version)


def install_package(package_name, version, install_latest):
  package = get_package_info(package_name, version, install_latest)
  subprocess.run(["pip", "install", package])


def get_installed_package_version(package_name):
  result = subprocess.run(["pip", "show", package_name], capture_output=True, text=True)
  result = result.stdout.lower().split("\n")
  version_index = [r for r in result if "version" in r]
  return version_index[0].split("version:")[1].strip()


def update_requirements(package_name):
  version = get_installed_package_version(package_name)
  package = generate_package_str(package_name, version)

  try:
    with open(FILE_PATH, "r+") as f:
      content = f.read()
      match = re.findall(f"{package_name}.*", content)

      if not match or len(match) == 0:
        content += f"{package}\n"
      else:
        content = content.replace(match[0], package)

      f.seek(0)
      f.write(content)
  except:
    with open(FILE_PATH, "w") as f:
      f.write(f"{package}\n")


if __name__ == "__main__":
  package_name = get_arg(1, True)

  version = get_arg(2)
  if version == LATEST_SWITCH:
    version = ""

  install_latest = get_arg(3)
  if not version:
    install_latest = get_arg(2)

  install_package(package_name, version, install_latest)

  update_requirements(package_name)
