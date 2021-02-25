import shutil
import glob
import pathlib
import configparser

import git
import yaml

def main():
    """Generate 3 files containing CSC versions for each deployment location.
    """
    # clone the repositories
    try:
        argo_cd_csc_repo = git.repo.base.Repo.clone_from("https://github.com/lsst-ts/argocd-csc", "argocd-csc")
        ts_cycle_build_repo = git.repo.Repo.clone_from("https://github.com/lsst-ts/ts_cycle_build", "ts_cycle_build")
    except git.exc.GitCommandError:
        pass
    # Pull the remote
    origin = ts_cycle_build_repo.remotes.origin
    origin.pull()
    # Glob the yaml files for each CSC
    values_paths = glob.glob("argocd-csc/apps/*/values-*.yaml")
    # Open a file to write down the relevant information
    with open("data.txt", "w") as df:
        for path in values_paths:
            with open(path) as f:
                name = pathlib.Path(f.name).stem
                csc_name = pathlib.Path(f.name).parents[0].stem
                yf = yaml.safe_load(f)
                # Try to get the tag from the file
                # If not found, don't write it
                try:
                    tag = yf["csc"]["image"]["tag"]
                except KeyError:
                    tag = None
                if tag is not None:
                    df.write(f"{csc_name} {name} {tag}\n")
    # Open the three deployment information files
    bts = open("base-teststand.txt", "w")
    ncsats = open("ncsa-teststand.txt", "w")
    summit = open("summit.txt", "w")
    with open("data.txt", "r") as df:
        for line in df:
            split_line = line.rstrip('\n').split(" ")
            csc_name, name, tag = split_line
            corrected_name = name.split("-")[1:]
            # Name of the deployment location
            corrected_name = '-'.join(corrected_name)
            if tag.startswith("c"):
                # cycle tag
                corrected_tag = tag[1:]
                git_tag = f"cycle-{corrected_tag}"
                # If no tag found, use the master branch
                try:
                    ts_cycle_build_repo.git.checkout(git_tag)
                except git.exc.GitCommandError:
                    ts_cycle_build_repo.git.checkout("master")
                # Work around ConfigReader expecting a [section_header]
                with open("ts_cycle_build/cycle/cycle.env", "r") as f:
                    config_string = '[dummy_section]\n' + f.read()
                config = configparser.ConfigParser()
                config.read_string(config_string)
                # Find the CSC version, some of the name listed are different
                # than the one in cycle build
                try:
                    csc_version = config["dummy_section"][f"ts_{csc_name}"]
                except KeyError:
                    if csc_name == "atmcs":
                        csc_version = config["dummy_section"]["ts_ATMCSSimulator"]
                    elif csc_name == "atpneumatics":
                        csc_version = config["dummy_section"]["ts_ATPneumaticsSimulator"]
                    elif csc_name == "atptg" or csc_name == "mtptg":
                        csc_version = config["dummy_section"]["ts_pointing_common"]
                    elif csc_name == "atqueue" or csc_name == "mtqueue":
                        csc_version = config["dummy_section"]["ts_scriptqueue"]
                    elif csc_name == "atscheduler" or csc_name == "mtscheduler":
                        csc_version = config["dummy_section"]["ts_scheduler"]
                    elif csc_name == "atspectrograph":
                        csc_version = config["dummy_section"]["ts_atspec"]
                    elif csc_name == "mtcamhexapod" or csc_name == "mtm2hexapod":
                        try:
                            csc_version = config["dummy_section"]["ts_mthexapod"]
                        except KeyError:
                            csc_version = config["dummy_section"]["ts_hexapod"]
                    elif csc_name == "mtdome":
                        pass
                    elif csc_name == "mtm1m3":
                        csc_version = config["dummy_section"]["ts_m1m3support"]
                    elif csc_name == "mtm2":
                        csc_version = config["dummy_section"]["ts_m2"]
                    elif csc_name == "mtrotator":
                        csc_version = config["dummy_section"]["ts_rotator"]
                    elif csc_name == "test-csc":
                        csc_version = config["dummy_section"]["ts_salobj"]
                    else:
                        raise
                version_information = f"{csc_name}={csc_version}\n"
                if corrected_name == "base-teststand":
                    bts.write(version_information)
                if corrected_name == "ncsa-teststand":
                    ncsats.write(version_information)
                if corrected_name == "summit":
                    summit.write(version_information)
    # clean up
    bts.close()
    ncsats.close()
    summit.close()
    shutil.rmtree(argo_cd_csc_repo.working_tree_dir)
    shutil.rmtree(ts_cycle_build_repo.working_tree_dir)


if __name__ == "__main__":
    main()
