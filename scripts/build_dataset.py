from newspace_twin.pipeline import run_pipeline

if __name__ == "__main__":
    print(run_pipeline(config_path="configs/base.yaml", stage="build_dataset"))
