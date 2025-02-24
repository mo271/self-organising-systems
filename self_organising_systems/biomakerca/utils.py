"""
Copyright 2023 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import time
import pkg_resources

from jax import vmap
import jax.random as jr
import jax.numpy as jp

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


vmap2 = lambda f: vmap(vmap(f))


def split_2d(key, w, h):
  return vmap(lambda k: jr.split(k, h))(jr.split(key, w))


def conditional_update(arr, idx, val, cond):
  """Update arr[idx] to val if cond is True."""
  return arr.at[idx].set((1 - cond) * arr[idx] + cond * val)


def stringify_class(instance, exclude_list=[], include_list=None):
  """Create a string that describes all class attributes and their values.
  
  Useful for printing classes for logging reasons.
  Arguments:
    instance: The class instance to stringify.
    exclude_list: list of attribute names to exclude (won't be put in the
      string).
    include_list: optional. If set to a list of strings, only attributes with
      these names will be added to the string.
  """
  return (
      type(instance).__name__ + ": {" +
      (", ".join(str(item[0])+ ": " + str(item[1]).replace("\n", ", ") for
                  item in vars(instance).items() if 
                  not callable(item) and(
                      (not include_list and item[0] not in exclude_list) or
                      (include_list and item[0] in include_list))))
      + "}")

def save_dna(dna, configuration_name, config, agent_logic, mutator, env_h=None,
             env_w=None, author="anonymous", notes="", out_dir="./"):
  """Save a dna (jp array) as a .npy file, and a .txt file with its details.
  
  This is the preferable way of storing information about a dna. It ensures that
  the file can be read as a numpy array, and it stores configuration information
  necessary for a proper usage of a dna in a .txt file.
  Essential information are:
  - EnvConfig used.
  - AgentLogic needed to reload the dna.
  - Mutator used.
  
  The file will be generated by concatenating configuration_name and a timestamp
  of the current time.
  
  Arguments:
    dna: the dna to save. Must be a np array.
    configuration_name: string that will be the prefix of the saved files.
      Should be a meaningful name, for instance a configuration name.
    config: the EnvConfig used with this dna.
    agent_logic: the AgentLogic used with this dna.
    mutator: the Mutator used with this dna
    env_h: optional information. The height of the environment.
    env_w: optional information. The width of the environment.
    author: metadata stating who the author is.
    notes: extra information that may be useful to write down.
    out_dir: where to write the files.
  
  Returns:
   the output file path (including the prefix identifier). To get the dna, 
    concatenate it with '.npy'. To get the metadata, concatenate it with '.txt'.
  """
  identifier = "_".join([configuration_name, str(time.time_ns())])

  out_file_path = out_dir + identifier
  with open(out_file_path + ".npy", "wb") as f:
    jp.save(f, dna, allow_pickle=False)
  # Write a txt file including information necessary for understanding the dna.

  lines = [
      "dna: %s" % identifier, str(config), str(agent_logic), str(mutator)]
  if env_h:
    lines.append("env_h: %s" % env_h)
  if env_w:
    lines.append("env_w: %s" % env_w)
  lines.append("author: %s" % author)
  lines.append("notes: %s" % notes)

  with open(out_file_path + ".txt", "w") as f:
    f.write("\n".join(lines))

  return out_file_path


def load_dna(file, load_from_this_package=True):
  """Load a dna from a .npy file.

  If load_from_this_package is True, we load from this package's dnalib dir.
  Otherwise, we load from the given file path.

  This is the recommended way to load a dna, since it doesn't allow pickle,
  which is a potential risk.
  If the file given is without the '.npy' suffix, it will be added.
  """
  if not file.lower().endswith(".npy"):
    file = file + ".npy"
  if load_from_this_package:
    # extract from dnalib
    resource_package = "self_organising_systems"
    resource_path = '/'.join(("biomakerca", "dnalib", file))
    fstream = pkg_resources.resource_stream(resource_package, resource_path)
    return jp.load(fstream, allow_pickle=False)
  with open(file, "rb") as f:
    return jp.load(f, allow_pickle=False)
  
