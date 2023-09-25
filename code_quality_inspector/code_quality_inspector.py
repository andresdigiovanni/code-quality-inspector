import csv
import os
from collections import defaultdict
from datetime import datetime
from statistics import mean

import git
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze


class CodeQualityInspector:
    """A class for inspecting and analyzing code quality metrics for a software project, which includes
    metrics such as cyclomatic complexity, maintainability, and lines of code."""

    def __init__(self, project_directory: str) -> None:
        self._project_directory = project_directory

        self._metrics: list = []
        self._metrics_by_file: list = []
        self._history_metrics: list = []
        self._history_metrics_by_file: dict = {}

    def inspect_project(
        self, inspect_history: bool = False, max_history_count: int = 0
    ) -> None:
        """
        Inspects the code quality metrics of the software project.

        Args:
            inspect_history (bool, optional): Whether to inspect historical metrics.
                If True, historical metrics will be collected. Defaults to False.
            max_history_count (int, optional): The maximum number of historical data points to consider.
                If provided, only the most recent 'max_history_count' data points will be analyzed.
                If not provided, all available historical data will be considered. Defaults to 0.

        Note: Inspecting the history of a large project can be time-consuming.

        Returns:
            None
        """

        self._generate_project_metrics_by_file()
        self._generate_project_metrics()

        if inspect_history:
            max_count = max_history_count if max_history_count > 0 else None
            self._history_metrics_by_file = self._generate_history_metrics_by_file(
                max_count=max_count
            )
            self._generate_history_metrics()

    def _generate_history_metrics_by_file(self, max_count):
        history_metrics_by_file = defaultdict(list)

        repo = git.Repo(self._project_directory)
        commits = repo.iter_commits(max_count=max_count)

        for commit in commits:
            for item in commit.tree.traverse():
                if item.type == "blob" and item.path.endswith(".py"):
                    file_date = datetime.fromtimestamp(commit.committed_date).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    file_name = os.path.splitext(item.name)[0]
                    file_content = repo.git.show(f"{commit.hexsha}:{item.path}")

                    if len(file_content) == 0 or file_name == "__init__":
                        continue

                    metrics = self._calculate_metrics(file_content, file_name)
                    metrics["Date"] = file_date

                    history_metrics_by_file[file_name].append(metrics)

        return history_metrics_by_file

    def _generate_history_metrics(self):
        metrics_by_date = defaultdict(list)

        for metrics_by_file in self._history_metrics_by_file.values():
            for metrics in metrics_by_file:
                metrics_by_date[metrics["Date"]].append(metrics)

        sorted_dates = sorted(metrics_by_date.keys(), reverse=True)

        for date in sorted_dates:
            date_metrics = metrics_by_date[date]
            total_ciclomatic = 0.0
            total_maintainability = 0.0
            total_loc = 0

            for metrics in date_metrics:
                total_ciclomatic += (
                    metrics["Ciclomatic_Complexity"] * metrics["Lines_of_Code"]
                )
                total_maintainability += (
                    metrics["Maintainability"] * metrics["Lines_of_Code"]
                )
                total_loc += metrics["Lines_of_Code"]

            weighted_avg_ciclomatic = total_ciclomatic / total_loc if total_loc else 0
            weighted_avg_maintainability = (
                total_maintainability / total_loc if total_loc else 0
            )

            self._history_metrics.append(
                {
                    "Date": date,
                    "Ciclomatic_Complexity": weighted_avg_ciclomatic,
                    "Maintainability": weighted_avg_maintainability,
                    "Lines_of_Code": total_loc,
                }
            )

    def _generate_project_metrics_by_file(self):
        history_metrics_by_file = self._generate_history_metrics_by_file(max_count=1)

        for file_name, file_metrics in history_metrics_by_file.items():
            metrics = file_metrics[0]
            metrics["File"] = file_name
            self._metrics_by_file.append(metrics)

    def _generate_project_metrics(self):
        total_ciclomatic = 0.0
        total_maintainability = 0.0
        total_loc = 0

        for metrics in self._metrics_by_file:
            total_ciclomatic += (
                metrics["Ciclomatic_Complexity"] * metrics["Lines_of_Code"]
            )
            total_maintainability += (
                metrics["Maintainability"] * metrics["Lines_of_Code"]
            )
            total_loc += metrics["Lines_of_Code"]

        weighted_avg_ciclomatic = total_ciclomatic / total_loc if total_loc else 0
        weighted_avg_maintainability = (
            total_maintainability / total_loc if total_loc else 0
        )

        self._metrics.append(
            {
                "Ciclomatic_Complexity": weighted_avg_ciclomatic,
                "Maintainability": weighted_avg_maintainability,
                "Lines_of_Code": total_loc,
            }
        )

    def _calculate_metrics(self, file_content: str, file_name: str) -> dict:
        try:
            cyclomatic_complexity_visit = cc_visit(file_content)
            if len(cyclomatic_complexity_visit):
                cyclomatic_complexity = mean(
                    x.complexity for x in cyclomatic_complexity_visit
                )
            else:
                cyclomatic_complexity = 0
            maintainability = mi_visit(file_content, multi=True)
            raw = analyze(file_content)
            num_lines_of_code = raw.loc

        except Exception as err:
            print("Error in {}: {}".format(file_name, err))
            cyclomatic_complexity = 0
            maintainability = 0
            num_lines_of_code = 0

        return {
            "Ciclomatic_Complexity": cyclomatic_complexity,
            "Maintainability": maintainability,
            "Lines_of_Code": num_lines_of_code,
        }

    def write_metrics_to_csv(self, output_directory: str):
        """
        Writes the collected code quality metrics to CSV files in the specified output directory.

        Args:
            output_directory (str): The directory where the CSV files will be saved.

        Returns:
            None
        """

        # Prepare directories
        output_metrics_csv = os.path.join(output_directory, "metrics.csv")
        output_metrics_by_file_csv = os.path.join(
            output_directory, "metrics_by_file.csv"
        )

        output_history_files_directory = os.path.join(output_directory, "files_history")
        output_history_csv = os.path.join(output_directory, "history_metrics.csv")

        os.makedirs(output_history_files_directory, exist_ok=True)

        # Write metrics
        self._write_to_csv(
            output_metrics_csv,
            [
                "Ciclomatic_Complexity",
                "Maintainability",
                "Lines_of_Code",
            ],
            self._metrics,
        )

        # Write files metrics
        self._write_to_csv(
            output_metrics_by_file_csv,
            [
                "File",
                "Date",
                "Ciclomatic_Complexity",
                "Maintainability",
                "Lines_of_Code",
            ],
            self._metrics_by_file,
        )

        # Write history files metrics
        for file_name, file_metrics in self._history_metrics_by_file.items():
            result_file_name = f"{file_name}.csv"
            result_file_path = os.path.join(
                output_history_files_directory, result_file_name
            )

            self._write_to_csv(
                result_file_path,
                [
                    "Date",
                    "Ciclomatic_Complexity",
                    "Maintainability",
                    "Lines_of_Code",
                ],
                file_metrics,
            )

        # Write history metrics
        self._write_to_csv(
            output_history_csv,
            [
                "Date",
                "Ciclomatic_Complexity",
                "Maintainability",
                "Lines_of_Code",
            ],
            self._history_metrics,
        )

    def _write_to_csv(self, path, fieldnames, content):
        with open(path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(content)
