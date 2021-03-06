#include <omp.h>
#include <stdio.h>
#include <time.h>
#include <iomanip>
#include <iostream>
#include <string.h>
#include <chrono>

using namespace std;
#define NUM_THREADS 4

void matMulSequential(double* op1Matrix, double* op2Matrix, double* resMatrix,
                  int matrixSize, int blockSize) {
  int ii, jj, kk, i, j, k, rowOffsetI, rowOffsetK;

  for (ii = 0; ii < matrixSize; ii += blockSize)
    for (jj = 0; jj < matrixSize; jj += blockSize)
      for (kk = 0; kk < matrixSize; kk += blockSize)
        for (i = ii; i < ii + blockSize; i++){
          rowOffsetI = i * matrixSize;
          for (k = kk; k < kk + blockSize; k++){
            rowOffsetK = k * matrixSize;
            for (j = jj; j < jj + blockSize; j++)
              resMatrix[rowOffsetI + j] +=
                  op1Matrix[rowOffsetI + k] *
                  op2Matrix[rowOffsetK + j];
          }
        }
}

void matMulParallelCollapse(double* op1Matrix, double* op2Matrix, double* resMatrix,
                  int matrixSize, int blockSize) {
  int ii, jj, kk, i, j, k, rowOffsetI, rowOffsetK;
  #pragma omp parallel shared(op1Matrix, op2Matrix, resMatrix) private(ii, jj, kk, i, j, k) num_threads(NUM_THREADS)
  { 
    #pragma omp for collapse(2)
    for (ii = 0; ii < matrixSize; ii += blockSize)
      for (jj = 0; jj < matrixSize; jj += blockSize)
        for (kk = 0; kk < matrixSize; kk += blockSize)
          for (i = ii; i < ii + blockSize; i++){
            rowOffsetI = i * matrixSize;
            for (k = kk; k < kk + blockSize; k++){
              rowOffsetK = k * matrixSize;
              for (j = jj; j < jj + blockSize; j++)
                resMatrix[rowOffsetI + j] +=
                    op1Matrix[rowOffsetI + k] *
                    op2Matrix[rowOffsetK + j];
            }
          }
  }

}

void matMulParallel(double* op1Matrix, double* op2Matrix, double* resMatrix,
                  int matrixSize, int blockSize) {
  int ii, jj, kk, i, j, k, rowOffsetI, rowOffsetK;
  #pragma omp parallel shared(op1Matrix, op2Matrix, resMatrix) private(ii, jj, kk, i, j, k) num_threads(NUM_THREADS)
  { 
    #pragma omp for
    for (ii = 0; ii < matrixSize; ii += blockSize)
      for (jj = 0; jj < matrixSize; jj += blockSize)
        for (kk = 0; kk < matrixSize; kk += blockSize)
          for (i = ii; i < ii + blockSize; i++){
            rowOffsetI = i * matrixSize;
            for (k = kk; k < kk + blockSize; k++){
              rowOffsetK = k * matrixSize;
              for (j = jj; j < jj + blockSize; j++)
                resMatrix[rowOffsetI + j] +=
                    op1Matrix[rowOffsetI + k] *
                    op2Matrix[rowOffsetK + j];
            }
          }
  }

}

/* Usage: matrixprod <square matrix size> <runs> <operation> [block size]*/
int main(int argc, char *argv[]) {
  if (argc < 3) {
    cerr << "ERROR: insufficient number of arguments (square matrix size, runs, operation)" << endl;
    return -1;
  }

  // Get arguments
  int matrixSize = atoi(argv[1]);
  int op = atoi(argv[2]);
  int runs = atoi(argv[3]);
  int blockSize = argc == 5 ? atoi(argv[4]) : matrixSize*matrixSize;

  const int MATRIX_SIZE_BYTES = (matrixSize * matrixSize) * sizeof(double);

  // init matrices
  double * op1Matrix = (double *)malloc(MATRIX_SIZE_BYTES);
  double * op2Matrix = (double *)malloc(MATRIX_SIZE_BYTES);
  double * resMatrix = (double *)malloc(MATRIX_SIZE_BYTES);


  for (int i = 0; i < matrixSize; i++){
    for (int j = 0; j < matrixSize; j++){
      op1Matrix[i * matrixSize + j] = (double)1.0;
      op2Matrix[i * matrixSize + j] = (double)(i + 1);
    }
  }

  for(int i = 0; i < runs; i++) {
    memset(resMatrix, 0, matrixSize * matrixSize * sizeof(double));
    // Start counting

    auto begin = std::chrono::high_resolution_clock::now();
    switch (op) {
      case 1:
        matMulSequential(op1Matrix, op2Matrix, resMatrix, matrixSize, blockSize);
        break;
      case 2:
        matMulParallel(op1Matrix, op2Matrix, resMatrix, matrixSize, blockSize);
        break;
      case 3:
        matMulParallelCollapse(op1Matrix, op2Matrix, resMatrix, matrixSize, blockSize);
        break;
    }
    auto end = chrono::high_resolution_clock::now();
    auto elapsed = chrono::duration_cast<chrono::microseconds>(end - begin);
    memset(resMatrix, 0, MATRIX_SIZE_BYTES);
    cout << op << " " << matrixSize << " " << blockSize << " " << elapsed.count()/ 1000000.0 << " " << NUM_THREADS << endl;
  }

  free(op1Matrix);
  free(op2Matrix);
  free(resMatrix);
  return 0;
}