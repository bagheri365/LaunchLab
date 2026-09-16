from launchlab.publication_figures import (
    write_delay_crossover_svg,
    write_misspecification_heatmap_svg,
    write_policy_region_svg,
    write_sample_size_policy_svg,
)
from launchlab.publication_narrative import build_publication_results


def fixture_tables(tmp_path):
    joint = tmp_path / "joint.csv"
    joint.write_text(
        "treatment_effect,n_users,assumed_value_multiplier,"
        "assumed_cost_multiplier,inconclusive_cost,policy,mean_regret\n"
        "0.0008,50000,1,1,1000,practical_significance,1000\n"
        "0.0008,100000,1,1,1000,economic_break_even,900\n"
        "0.0010,50000,1,1,1000,statistical_superiority,800\n"
        "0.0010,100000,1,1,1000,statistical_superiority,700\n",
        encoding="utf-8",
    )

    delay = tmp_path / "delay.csv"
    delay.write_text(
        "treatment_effect,inconclusive_cost,"
        "minimum_positive_value_probability,mean_regret\n"
        "0.0008,0,0.99,400\n"
        "0.0008,75000,0.975,70000\n"
        "0.0010,0,0.99,800\n"
        "0.0010,75000,0.90,70000\n",
        encoding="utf-8",
    )

    misspec = tmp_path / "misspec.csv"
    misspec.write_text(
        "assumed_value_multiplier,assumed_cost_multiplier,policy,"
        "correct_decision_rate,harmful_launch_rate,missed_opportunity_rate,"
        "inconclusive_rate,mean_regret\n"
        "0.5,0.5,economic_break_even,0,0,0,1,1000\n"
        "0.5,1.5,economic_break_even,0,0,0,1,100000\n"
        "1.0,0.5,economic_break_even,0,0,0,1,2000\n"
        "1.0,1.5,economic_break_even,0,0,0,1,50000\n",
        encoding="utf-8",
    )
    return joint, delay, misspec


def test_publication_svgs(tmp_path):
    joint, delay, misspec = fixture_tables(tmp_path)

    paths = [
        write_policy_region_svg(joint, tmp_path / "policy.svg"),
        write_delay_crossover_svg(delay, tmp_path / "delay.svg"),
        write_misspecification_heatmap_svg(misspec, tmp_path / "heat.svg"),
        write_sample_size_policy_svg(joint, tmp_path / "sample.svg"),
    ]

    for path in paths:
        text = path.read_text()
        assert text.startswith("<svg")
        assert "</svg>" in text


def test_publication_narrative(tmp_path):
    joint, delay, misspec = fixture_tables(tmp_path)

    text = build_publication_results(
        joint_optima_csv=joint,
        delay_optima_csv=delay,
        misspecification_csv=misspec,
    )

    assert "no single launch rule" in text.lower()
    assert "$75,000" in text
    assert "economic break-even policy" in text
