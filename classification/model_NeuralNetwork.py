import dataset_transforms as datum
import numpy              as np

# The domain specific dependencies.
from sklearn.neural_network import MLPClassifier
from sklearn                import metrics
from scipy                  import stats


#################################
###   Data preparation
#################################

monster_data = datum.retreive_monster_dataset(tagged_trait=True, standardized_label_classes=5, decorrelate=0.6)

# Split off the last column as the label vector.
X, Y = datum.seperate_data(monster_data)

# Partition out data into training, validation and testing sets.
X_train_full, X_train_part, X_valid, X_test, Y_train_full, Y_train_part, Y_valid, Y_test = datum.train_valid_test(X, Y, 0.2, 0.2)


#################################
###   Model Selection
#################################

# First, we want to determine the best hyperparameters.
# To do so we generate a list of potential values.
param_grid =    { 'activation'     : ['identity', 'logistic', 'tanh', 'relu']
                , 'solver'         : ['lbfgs', 'sgd', 'adam']
                , 'alpha'          : [10**(i - 4) for i in range(0,9)]
                , 'learning_rate'  : ['constant', 'invscaling', 'adaptive'] 
                , 'early_stopping' : [False, True]
                , 'random_state'   : [datum.STATIC_SEED]
                }

best_hyperparameters =  { 'activation'     : 'logistic'
                        , 'solver'         : 'adam'
                        , 'alpha'          : 0.1
                        , 'learning_rate'  : 'constant'
                        , 'early_stopping' : False
                        , 'random_state'   : datum.STATIC_SEED
                        }

# If we don't already have best parameters...
# Let's go find them!
if best_hyperparameters == None:
    best_hyperparameters = datum.model_selection(MLPClassifier(), param_grid, X_train_part, Y_train_part)

classifier_NB = MLPClassifier(**best_hyperparameters)
Y_score = classifier_NB.fit(X_train_part, Y_train_part) 

print("Built the support vector model")
print("Using hyperparameters:")
for k,v in best_hyperparameters.items():
    print(" ",k,"=",v)
datum.describe_data_set(X_train_part, "Partial training set containing:")
print()


#################################
###   Construct Classifier
#################################

# Build a new classifier using the entire training set.
# Incorperate what we learned during hyperparameter tuning
# and classifier perfomance evaluation.
classifier_NB = MLPClassifier(**best_hyperparameters)
classifier_NB.fit(X_train_full, Y_train_full)

print("Built the support vector classifier")
print("Using hyperparameters:")
for k,v in best_hyperparameters.items():
    print(" ",k,"=",v)
datum.describe_data_set(X_train_full, "Utilizing the full training set containing:")
print()

Y_score = classifier_NB.predict(X_test)

datum.describe_data_set(X_test, "Generated predictions for the test data set containing:")

def inspect_confusion_matrix(Y_true, Y_pred):
    matrix = metrics.confusion_matrix(Y_true, Y_pred)
    maxVal = max(np.concatenate(matrix).flat, key=lambda x: x)
    padLen = len(str(maxVal))
    
    print("Confusion matrix:")
    for row in matrix:
        print("  ", sep='', end='')
        for col in row:
            print(str(col).rjust(padLen), " ", sep='', end='')
        print()

inspect_confusion_matrix(Y_test, Y_score)

print("Precision Score:", round(metrics.precision_score(Y_test, Y_score, average='weighted'), 4))
print("Recall Score:   ", round(metrics.recall_score(   Y_test, Y_score, average='weighted'), 4))
print("F1 Score:       ", round(metrics.f1_score(       Y_test, Y_score, average='weighted'), 4))
