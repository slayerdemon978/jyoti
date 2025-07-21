import tensorflow as tf
import tensorflow_quantum as tfq
import cirq
import sympy
import numpy as np
import matplotlib.pyplot as plt
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
    for x in data:
        # Create a circuit with the same structure but with data-specific parameters
        param_resolver = dict(zip(inputs, x))
        resolved_circuit = cirq.resolve_parameters(circuit, param_resolver)
        circuits.append(resolved_circuit)
    return tfq.convert_to_tensor(circuits)

X_train_circuits = encode_data_to_circuits(X_train_pca)
X_test_circuits = encode_data_to_circuits(X_test_pca)

# Build the model
input_circuits = tf.keras.layers.Input(shape=(), dtype=tf.string, name='circuits_input')

# PQC layer
pqc = tfq.layers.PQC(circuit, readouts)
pqc_output = pqc(input_circuits)
output = tf.keras.layers.Dense(10, activation='softmax')(pqc_output)

model = tf.keras.Model(inputs=input_circuits, outputs=output)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# Training (small batch for testing)
batch_train = 500
batch_val = 100

history = model.fit(
    x=X_train_circuits[:batch_train],
    y=Y_train_oh[:batch_train],
    validation_data=(
        X_test_circuits[:batch_val],
        Y_test_oh[:batch_val]
    ),
    epochs=5,
    batch_size=32,
    callbacks=[TqdmCallback(verbose=1)]
)

# Evaluate the model on test data
test_loss, test_accuracy = model.evaluate(
    X_test_circuits,
    Y_test_oh,
    verbose=1
)
print(f"Test accuracy: {test_accuracy:.4f}")

# We'll skip saving the model due to compatibility issues with TensorFlow Quantum
# Instead, let's save the model weights
model.save_weights('quantum_fashion_mnist_weights')
print("Model weights saved successfully!")

# Plot training history
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.savefig('training_history.png')
plt.close()
print("Training history plot saved as 'training_history.png'")

# Let's also visualize some predictions
n_samples = 5
test_samples = X_test_circuits[:n_samples]
predictions = model.predict(test_samples)
predicted_classes = np.argmax(predictions, axis=1)
actual_classes = np.argmax(Y_test_oh[:n_samples], axis=1)

plt.figure(figsize=(15, 3))
for i in range(n_samples):
    plt.subplot(1, n_samples, i+1)
    plt.imshow(X_test[i], cmap='gray')
    plt.title(f"Pred: {predicted_classes[i]}\nTrue: {actual_classes[i]}")
    plt.axis('off')
plt.tight_layout()
plt.savefig('predictions.png')
plt.close()
print("Predictions visualization saved as 'predictions.png'")
