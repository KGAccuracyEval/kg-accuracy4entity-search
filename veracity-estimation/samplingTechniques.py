import random

from scipy import stats


class SRSSampler(object):
    """
    This class represents the Simple Random Sampling (SRS) scheme used to perform KG accuracy evaluation.
    The SRS estimator is an unbiased estimator.
    """

    def __init__(self, alpha=0.05):
        """
        Initialize the sampler and set confidence level plus Normal critical value z with right-tail probability αlpha/2

        :param alpha: the user defined confidence level
        """

        # confidence level
        self.alpha = alpha
        self.z = stats.norm.isf(self.alpha/2)

    @staticmethod
    def estimate(sample):
        """
        Estimate the KG accuracy based on sample

        :param sample: input sample (i.e., set of triples) used for estimation
        :return: KG accuracy estimate
        """

        return sum(sample)/len(sample)

    def computeVar(self, sample):
        """
        Compute the sample variance

        :param sample: input sample (i.e., set of triples) used for estimation
        :return: sample variance
        """

        # estimate mean
        ae = self.estimate(sample)
        # count number of clusters in sample
        n = len(sample)
        # compute variance
        var = (1/n) * (ae * (1-ae))
        return var

    def computeCI(self, sample):
        """
        Compute Confidence Interval (CI)

        :param sample: input sample (i.e., set of triples) used for estimation
        :return: the CI as (lowerBound, upperBound)
        """

        # compute mean estimate
        ae = self.estimate(sample)

        n = len(sample)
        x = sum(sample)

        # compute the adjusted sample size
        n_ = n + self.z ** 2
        # compute the adjusted number of successes
        x_ = x + (self.z ** 2) / 2
        # compute the adjusted mean estimate
        ae_ = x_ / n_

        # compute the margin of error
        moe = ((self.z * (n ** 0.5)) / n_) * (((ae * (1 - ae)) + ((self.z ** 2) / (4 * n))) ** 0.5)

        if (n <= 50 and x in [1, 2]) or (n >= 51 and x in [1, 2, 3]):
            lowerB = 0.5 * stats.chi2.isf(q=1 - self.alpha, df=2 * x) / n
        else:
            lowerB = max(0, ae_ - moe)  # max used to avoid floating points rounding errors

        if (n <= 50 and x in [n - 1, n - 2]) or (n >= 51 and x in [n - 1, n - 2, n - 3]):
            upperB = 1 - (0.5 * stats.chi2.isf(q=1 - self.alpha, df=2 * (n - x))) / n
        else:
            upperB = min(1, ae_ + moe)  # min used to avoid floating points rounding errors

        # return CI as (lowerBound, upperBound)
        return lowerB, upperB

    @staticmethod
    def annotateFact(factID, fact):
        """
        Perform fact annotation
        :param factID: id of target fact
        :param fact: the target fact (s, p, o)
        :return: veracity annotation (0/1 label)
        """

        userInput = input("{}\t{}:".format(factID, fact))
        # validate user input
        while userInput not in ['0', '1']:
            print('Invalid input. Please, enter 0 for incorrect and 1 for correct.')
            userInput = input("{}\t{}:".format(factID, fact))

        # store annotation
        annotation = int(userInput)
        return annotation

    @staticmethod
    def costFunction(entities, triples, c1=45, c2=25):
        """
        Compute the annotation cost function (in hours)

        :param entities: num of entities
        :param triples: num of triples
        :param c1: average cost for Entity Identification (EI)
        :param c2: average cost for Fact Verification (FV)
        :return: the annotation cost function (in hours)
        """

        return (entities * c1 + triples * c2) / 3600

    def run(self, kg, stratumID, minSample=30, thrMoE=0.05, c1=45, c2=25):
        """
        Run the evaluation procedure on KG w/ SRS and stop when MoE < thr
        :param kg: the target KG
        :param stratumID: the id of the considered partition -- which represents the current KG
        :param minSample: the min sample size required to trigger the evaluation procedure
        :param thrMoE: the user defined MoE threshold
        :param c1: average cost for Entity Identification (EI)
        :param c2: average cost for Fact Verification (FV)
        :return: evaluation statistics
        """

        # set params
        lowerB = 0.0
        upperB = 1.0
        entities = {}
        sample = {}

        print('Annotate facts w/ 0 for incorrect and 1 for correct.')

        # open output file for writing
        with open('../data/annotations/facts/partition'+str(stratumID)+'.tsv', 'w') as out:
            # write header to output file
            out.write("id\tveracity\n")

            while (upperB-lowerB)/2 > thrMoE:  # stop when MoE gets lower than threshold
                # perform SRS over the KG
                factID, fact = random.choices(population=kg, k=1)[0]

                if factID in sample:  # found annotated fact -- skip it
                    continue

                if fact[0] not in entities:  # found new (head) entity -- add to entities
                    entities[fact[0]] = 1

                # get annotations for triples within sample
                factVeracity = self.annotateFact(factID, fact)
                sample[factID] = factVeracity

                if len(sample) >= minSample:  # compute CI
                    lowerB, upperB = self.computeCI(list(sample.values()))

                # write fact to output file
                out.write("{}\t{}\n".format(factID, factVeracity))

        # compute KG accuracy estimate
        estimate = self.estimate(list(sample.values()))
        # compute cost function
        cost = self.costFunction(len(entities), len(sample), c1, c2)

        # store KG accuracy stats (w/o annotation cost)
        with open('../data/stats/facts/partition'+str(stratumID)+'.tsv', 'w') as out:
            out.write("estimate\tlowerBound\tupperBound\n")
            out.write("{}\t{}\t{}\n".format(estimate, lowerB, upperB))

        # return the annotated sample together w/ stats
        return sample, (estimate, (lowerB, upperB), cost)
