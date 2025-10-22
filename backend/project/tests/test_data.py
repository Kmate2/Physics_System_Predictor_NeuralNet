import os
import tempfile
import pandas as pd
from training.data import simulate_projectile_data, load_or_simulate_dataframe


def test_simulate_projectile_data_shape():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test_data.csv")
        df = simulate_projectile_data(n=100, path=path, rng_seed=42)

        assert len(df) == 100
        assert list(df.columns) == ["velocity", "angle_deg", "range", "max_height", "flight_time"]


def test_simulate_projectile_data_physics():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test_data.csv")
        df = simulate_projectile_data(n=50, path=path, rng_seed=42)

        assert (df["velocity"] > 0).all()
        assert (df["angle_deg"] > 0).all()
        assert (df["range"] >= 0).all()
        assert (df["max_height"] >= 0).all()
        assert (df["flight_time"] >= 0).all()

        assert (df["velocity"] >= 10).all() and (df["velocity"] <= 100).all()
        assert (df["angle_deg"] >= 10).all() and (df["angle_deg"] <= 80).all()


def test_simulate_projectile_data_file_creation():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "subdir", "test_data.csv")
        df = simulate_projectile_data(n=20, path=path, rng_seed=42)


        assert os.path.exists(path)

        df_loaded = pd.read_csv(path)
        assert len(df_loaded) == 20
        pd.testing.assert_frame_equal(df, df_loaded)


def test_simulate_projectile_data_reproducibility():
    with tempfile.TemporaryDirectory() as tmpdir:
        path1 = os.path.join(tmpdir, "test1.csv")
        path2 = os.path.join(tmpdir, "test2.csv")

        df1 = simulate_projectile_data(n=50, path=path1, rng_seed=123)
        df2 = simulate_projectile_data(n=50, path=path2, rng_seed=123)

        pd.testing.assert_frame_equal(df1, df2)


def test_load_or_simulate_dataframe_existing():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "existing.csv")

        df_original = simulate_projectile_data(n=30, path=path, rng_seed=42)

        df_loaded = load_or_simulate_dataframe(path=path)

        pd.testing.assert_frame_equal(df_original, df_loaded)


def test_load_or_simulate_dataframe_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "nonexistent.csv")

        assert not os.path.exists(path)

        df = load_or_simulate_dataframe(path=path)

        assert os.path.exists(path)
        assert len(df) == 2000