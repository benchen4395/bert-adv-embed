import numpy as np

def to_sent(x, unvocab, tokenized=False):
    '''
    Converts the given input into a sentence.
    '''
    if type(x) == tuple:
        return to_sent(x[0], unvocab, tokenized)
    if type(x) == int:
        return to_sent([x], unvocab, tokenized)
    if type(x) == list:
        toks = [unvocab[w] for w in x]
        if tokenized:
            return toks
        else:
            return ' '.join(toks)
    return to_sent(x.tolist(), unvocab, tokenized)

def vec_normalize(vec, xp=np, epsilon=1e-12):
    '''
    Normalizes the given vector.
    '''
    return vec / (xp.linalg.norm(vec) + epsilon)

def mat_normalize(mat, xp=np, epsilon=1e-12):
    '''
    Normalizes the columns of the given matrix.
    '''
    return mat / (xp.linalg.norm(mat, axis=1)[:, xp.newaxis] + epsilon)

def nn_vec(mat, vec, k=1, normalize=True, return_vals=False, xp=np):
    '''
    Computes nearest neighbors (in terms of cosine similarity) 
    of the given vector in columns of the given matrix.
    '''
    if normalize:
        mat = mat_normalize(mat, xp=xp)
        vec = vec_normalize(vec, xp=xp)
    cosines = xp.matmul(mat, vec)

    if k==1:    # Return the most similar element
        nns = xp.argmax(cosines)
    else:       # Calculate nearest neighbors
        nns = xp.argsort(-cosines)[:k]
    
    if return_vals:
        return nns, cosines[nns]
    else:
        return nns

def nn_vec_L2(mat, vec, k=1, return_vals=False, xp=np):
    '''
    Computes nearest neighbors (in terms of cosine similarity) 
    of the given vector in columns of the given matrix.
    '''
    norms = xp.linalg.norm(mat - vec, axis=1)

    if k==1:    # Return the most similar element
        nns = xp.argmin(norms)
    else:       # Calculate nearest neighbors
        nns = xp.argsort(norms)[:k]
    
    if return_vals:
        return nns, norms[nns]
    else:
        return nns
