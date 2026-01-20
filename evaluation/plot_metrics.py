import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_charts(csv_path="evaluation/results.csv", output_dir="evaluation/charts"):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load Data
    df = pd.read_csv(csv_path)
    
    # Configure Style
    sns.set_theme(style="whitegrid")
    
    # 1. Answer Relevancy Distribution (Boxplot + Swarm)
    plt.figure(figsize=(8, 6))
    plt.title("Distribution of Answer Relevancy Scores", fontsize=16)
    sns.boxplot(y=df["answer_relevancy"], color="lightblue", showfliers=False)
    sns.swarmplot(y=df["answer_relevancy"], color="darkblue", size=8)
    plt.ylabel("Relevancy Score (0-1)", fontsize=12)
    plt.ylim(0, 1.1)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/relevancy_distribution.png", dpi=300)
    print(f"Generated: {output_dir}/relevancy_distribution.png")
    
    # 2. Relevancy per Question (Bar Chart)
    # Truncate questions for display
    # RAGAS 0.x uses 'user_input' column for questions usually
    col_question = "user_input" if "user_input" in df.columns else "question"
    
    df["short_question"] = df[col_question].apply(lambda x: x[:30] + "..." if len(x) > 30 else x)
    
    plt.figure(figsize=(10, 6))
    barplot = sns.barplot(x="answer_relevancy", y="short_question", data=df, palette="viridis", orient="h")
    plt.title("Answer Relevancy per Question", fontsize=16)
    plt.xlabel("Relevancy Score", fontsize=12)
    plt.ylabel("Question", fontsize=12)
    plt.xlim(0, 1.1)
    
    # Add labels
    for i, p in enumerate(barplot.patches):
        width = p.get_width()
        plt.text(width + 0.02, p.get_y() + p.get_height()/2 + 0.1, f'{width:.2f}', ha='left')

    plt.tight_layout()
    plt.savefig(f"{output_dir}/relevancy_per_question.png", dpi=300)
    print(f"Generated: {output_dir}/relevancy_per_question.png")

if __name__ == "__main__":
    generate_charts()
