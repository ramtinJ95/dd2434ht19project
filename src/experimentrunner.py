from dataloaders.newsgroupdatasetloader import NewsGroupDatasetLoader
import gin
import data_utils
from svm import SVM
import numpy as np
from kernels import ClusterKernel

@gin.configurable
def train_svm(datasetLoader, test_points, data_limit=0):
    input, output = datasetLoader.get_full_dataset()
    if data_limit != 0:
        input = input[:data_limit, :]
        output = output[:data_limit]

    input, output = data_utils.construct_one_vs_all(input, output, 0)
    (input_train, input_test, output_train, output_test) = data_utils.split(input, output, test_points)
    #Run svm
    svm = SVM()
    svm.give_training_data(input_train, output_train)
    svm.train()

    svm.give_test_data(input_test, output_test)
    svm.analyze()

@gin.configurable
class ExperimentRunner:
    def __init__(self, experiment='single_run_newspaper'):
        self.experiment = experiment
    
    def RunExperiment(self):
        if self.experiment == 'single_run_newspaper':
            #Now we can load the data.
            datasetLoader = NewsGroupDatasetLoader()
            datasetLoader.load_dataset()
            
            train_svm(datasetLoader)
        elif self.experiment == 'figure_2':
            datasetLoader = NewsGroupDatasetLoader()
            datasetLoader.load_dataset()
            kernel = ClusterKernel()
            input, output = datasetLoader.get_full_dataset()
            input, output = data_utils.construct_one_vs_all(input, output, 0)

            (input_train, input_test, output_train, output_test) = data_utils.split(input, output, 768)
            kernel_fun = kernel.kernel(input)
            svm = SVM()

            #Send the data and unlabeled data (testing is analysed as unlabeled data)
            svm.set_kernel(kernel_fun)

            #Send the indexes of labeled training data and the labels
            training_indexes = np.asarray(list(range(128)))
            svm.give_training_data(training_indexes, output[0:128])

            #Train the SVM.
            svm.train()

            #Send the indexes of labeled testing data and the labels
            testing_indexes = np.asarray(list(range(128,256)))
            svm.give_test_data(testing_indexes, output[128:256])
            svm.analyze()

            #Todo: Construct kernel for each type of kernel function.
            #Todo: Average test error over 100 random selections of labelled points, ranging from 2->128.
            #reuse the same kernel.
            #(ie 100 runs with 2, 100 runs with 4, 8, 16, 32, 64, 128)
            #Todo: Visualize and evaluate eigenvalue sizes also.
