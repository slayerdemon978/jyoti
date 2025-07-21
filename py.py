import tensorflow as tf
import tensorflow_quantum as tfq
import cirq
import sympy
import numpy as np
from sklearn.decomposition import PCA
from tqdm.keras import TqdmCallback

# Data
from tensorflow.keras.datasets import fashion_mnist as data

(X_train, Y_train), (X_test, Y_test) = data.load_data()
X_train = X_train / 255.0
X_test = X_test / 255.0
Y_train = Y_train.astype('int')
Y_test = Y_test.astype('int')
X_train_flat = X_train.reshape(-1, 28 * 28)
X_test_flat = X_test.reshape(-1, 28 * 28)
X_train_flat = 2 * X_train_flat - 1  # Scale to [-1, 1]
X_test_flat = 2 * X_test_flat - 1
Y_train_oh = tf.keras.utils.to_categorical(Y_train, num_classes=10)
Y_test_oh = tf.keras.utils.to_categorical(Y_test, num_classes=10)

# PCA
n_qubits = 4
pca = PCA(n_components=n_qubits)
X_train_pca = pca.fit_transform(X_train_flat)
X_test_pca = pca.transform(X_test_flat)
X_train_pca = (X_train_pca - X_train_pca.min()) / (X_train_pca.max() - X_train_pca.min()) * np.pi  # Scale to [0, π]
X_test_pca = (X_test_pca - X_test_pca.min()) / (X_test_pca.max() - X_test_pca.min()) * np.pi

# Quantum Circuit
qubits = [cirq.GridQubit(0, i) for i in range(n_qubits)]
inputs = sympy.symbols(f'x0:{n_qubits}')
weights = sympy.symbols(f'w0:{n_qubits}')

circuit = cirq.Circuit()
for i, q in enumerate(qubits):
    circuit.append(cirq.ry(inputs[i])(q))  # Data-encoding gates
    circuit.append(cirq.rx(weights[i])(q))  # Trainable gates
for i in range(n_qubits - 1):
    circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))  # Entanglement
readouts = [cirq.Z(q) for q in qubits]  # Measurements

print("Quantum circuit:")
print(circuit)

# Convert data to quantum circuits (correctly batched)
def encode_data_to_circuits(data):
    """Convert classical data to quantum circuits."""
    circuits = []
    for _ in range(data.shape[0]):
        circuits.append(circuit)
    return tfq.convert_to_tensor(circuits)

X_train_circuits = encode_data_to_circuits(X_train_pca)
X_test_circuits = encode_data_to_circuits(X_test_pca)

# Build the model correctly
input_circuits = tf.keras.layers.Input(shape=(), dtype=tf.string, name='circuits_input')
input_params = tf.keras.layers.Input(shape=(n_qubits,), dtype=tf.float32, name='params_input')

# PQC layer (critical fix: pass inputs as a LIST)
pqc_output = tfq.layers.PQC(circuit, readouts)([input_circuits, input_params])
output = tf.keras.layers.Dense(10, activation='softmax')(pqc_output)

model = tf.keras.Model(inputs=[input_circuits, input_params], outputs=output)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# Training (small batch for testing)
batch_train = 500
batch_val = 100

history = model.fit(
    x=[X_train_circuits[:batch_train],  # Circuits (as strings)
    y=Y_train_oh[:batch_train],
    validation_data=(
        [X_test_circuits[:batch_val]],  # Validation circuits
        Y_test_oh[:batch_val]
    ),
    epochs=5,
    batch_size=32,
    callbacks=[TqdmCallback(verbose=1)]
)
