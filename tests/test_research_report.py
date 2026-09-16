from launchlab.research_report import (
    build_research_summary,
    render_research_summary_markdown,
    write_research_summary,
)


def write_fixture_tables(root):
    root.mkdir(parents=True, exist_ok=True)

    (root / "joint_decision_optima.csv").write_text(
        "treatment_effect,n_users,assumed_value_multiplier,"
        "assumed_cost_multiplier,inconclusive_cost,policy,mean_regret\n"
        "0.0008,100000,1.0,1.0,1000,practical_significance,1000\n"
        "0.0010,100000,1.0,1.0,1000,statistical_superiority,900\n"
        "0.0010,200000,1.0,1.0,1000,economic_break_even,800\n",
        encoding="utf-8",
    )

    (root / "delay_cost_optima.csv").write_text(
        "treatment_effect,inconclusive_cost,"
        "minimum_positive_value_probability,mean_regret\n"
        "0.0008,0,0.99,400\n"
        "0.0008,75000,0.975,74250\n"
        "0.0010,0,0.99,800\n"
        "0.0010,75000,0.90,75050\n",
        encoding="utf-8",
    )

    (root / "economic_misspecification.csv").write_text(
        "assumed_value_multiplier,assumed_cost_multiplier,policy,"
        "correct_decision_rate,harmful_launch_rate,missed_opportunity_rate,"
        "inconclusive_rate,mean_regret\n"
        "1.0,1.0,economic_break_even,0.04,0,0.045,0.915,9915\n"
        "0.5,1.5,economic_break_even,0,0,0.595,0.405,119405\n"
        "1.0,1.0,statistical_superiority,0.19,0,0,0.81,810\n",
        encoding="utf-8",
    )


def test_build_summary(tmp_path):
    tables = tmp_path / "tables"
    write_fixture_tables(tables)

    summary = build_research_summary(tables)

    counts = dict(summary.joint_policy_counts)
    assert counts["statistical_superiority"] == 1
    assert counts["practical_significance"] == 1
    assert counts["economic_break_even"] == 1

    crossovers = {
        row.treatment_effect: row for row in summary.delay_crossovers
    }
    assert crossovers[0.0008].crossover_inconclusive_cost == 75000
    assert crossovers[0.0010].crossover_probability_threshold == 0.90


def test_markdown_contains_core_sections(tmp_path):
    tables = tmp_path / "tables"
    write_fixture_tables(tables)
    summary = build_research_summary(tables)

    markdown = render_research_summary_markdown(summary)

    assert "# LaunchLab Research Summary" in markdown
    assert "Minimum-regret policy regions" in markdown
    assert "Delay-cost crossover" in markdown
    assert "Economic misspecification regret range" in markdown


def test_write_summary(tmp_path):
    tables = tmp_path / "tables"
    write_fixture_tables(tables)
    summary = build_research_summary(tables)

    path = write_research_summary(
        summary,
        tmp_path / "reports" / "summary.md",
    )

    assert path.exists()
    assert "LaunchLab Research Summary" in path.read_text()
