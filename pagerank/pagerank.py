import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 1000000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    pw_link = corpus[page]
    prob_dict = dict()
    for link in corpus.keys():
        if link in pw_link:
            prob_dict[link] = damping_factor / len(pw_link) + (1 - damping_factor) / len(corpus)
        else:
            prob_dict[link] = (1 - damping_factor) / len(corpus)
    prob_sum = sum(prob_dict.values())
    for link in prob_dict:
        prob_dict[link] /= prob_sum
    return prob_dict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    PR = dict()
    for page in corpus:
        PR[page] = 0
    page = random.choice(list(corpus.keys()))
    for i in range(n):
        PR[page] += 1
        trans = transition_model(corpus, page, damping_factor)
        rand = random.random()
        for link in trans:
            rand -= trans[link]
            if rand < 0:
                page = link
                break
    for page in PR:
        PR[page] /= n
    return PR


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    PR = dict()
    for page in corpus:
        PR[page] = 1 / len(corpus)
    flag = True
    while flag:
        flag = False
        PR_new = dict()
        for page in corpus:
            PR_new[page] = (1 - damping_factor) / len(corpus)
        for page in corpus:
            for link in corpus[page]:
                PR_new[link] += damping_factor * PR[page]/ len(corpus[page])
        for page in PR:
            if abs(PR[page] - PR_new[page]) > 0.0001:
                flag = True
                break
        PR = PR_new
    PR_sum = sum(PR.values())
    for page in PR:
        PR[page] /= PR_sum
    return PR


if __name__ == "__main__":
    main()
