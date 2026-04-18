"""
3D Biometric Signature Verifier
Uses Dynamic Time Warping (DTW) to compare live 3D hand movements
against stored reference signatures.
"""

import json
import numpy as np
from pathlib import Path
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw


class SignatureVerifier:
    """
    Verifies 3D biometric signatures using Dynamic Time Warping.
    
    DTW allows for slight timing variations while maintaining shape similarity.
    This is crucial for biometric verification where users won't draw at
    exactly the same speed each time.
    """
    
    def __init__(self, reference_path, threshold=50.0, min_z_variance=100.0):
        """
        Args:
            reference_path: Path to reference signature JSON
            threshold: DTW distance threshold for acceptance (lower = stricter)
            min_z_variance: Minimum Z variance to prevent spoofing
        """
        self.reference_path = reference_path
        self.threshold = threshold
        self.min_z_variance = min_z_variance
        
        self.reference_signature = None
        self.reference_points = None
        
        self.load_reference()
    
    def load_reference(self):
        """Load reference signature from file."""
        if not Path(self.reference_path).exists():
            raise FileNotFoundError(f"Reference signature not found: {self.reference_path}")
        
        with open(self.reference_path, 'r') as f:
            self.reference_signature = json.load(f)
        
        # Extract 3D points as numpy array
        path = self.reference_signature['path']
        self.reference_points = np.array([
            [p['x'], p['y'], p['z']] for p in path
        ])
        
        print(f"[Verifier] Loaded reference: {len(self.reference_points)} points")
        print(f"[Verifier] Z-variance: {self.reference_signature['metadata']['z_variance']:.1f} mm²")
    
    def verify(self, candidate_path):
        """
        Verify a candidate signature against the reference.
        
        Args:
            candidate_path: List of dicts with x, y, z coordinates
        
        Returns:
            dict: {
                'verified': bool,
                'dtw_distance': float,
                'z_variance': float,
                'reason': str
            }
        """
        # Anti-spoofing: Check Z-axis variance
        z_values = [p['z'] for p in candidate_path]
        z_variance = np.var(z_values)
        
        if z_variance < self.min_z_variance:
            return {
                'verified': False,
                'dtw_distance': -1,
                'z_variance': z_variance,
                'reason': f'Flat signature (Z-var: {z_variance:.1f} < {self.min_z_variance})'
            }
        
        # Convert candidate to numpy array
        candidate_points = np.array([
            [p['x'], p['y'], p['z']] for p in candidate_path
        ])
        
        # Compute DTW distance
        distance, path = fastdtw(self.reference_points, candidate_points, dist=euclidean)
        
        # Normalize by path length
        normalized_distance = distance / len(candidate_path)
        
        verified = normalized_distance <= self.threshold
        
        result = {
            'verified': verified,
            'dtw_distance': float(normalized_distance),
            'z_variance': float(z_variance),
            'reason': 'Signature match' if verified else f'Distance too high: {normalized_distance:.2f} > {self.threshold}'
        }
        
        print(f"[Verifier] DTW distance: {normalized_distance:.2f}, Threshold: {self.threshold}")
        print(f"[Verifier] Z-variance: {z_variance:.1f} mm²")
        print(f"[Verifier] Result: {'✓ VERIFIED' if verified else '✗ REJECTED'}")
        
        return result
    
    def verify_euclidean(self, candidate_path, threshold_multiplier=1.5):
        """
        Alternative verification using simple Euclidean distance.
        Faster but less robust than DTW.
        
        Args:
            candidate_path: List of dicts with x, y, z coordinates
            threshold_multiplier: Multiplier for threshold
        
        Returns:
            dict: Verification result
        """
        # Anti-spoofing check
        z_values = [p['z'] for p in candidate_path]
        z_variance = np.var(z_values)
        
        if z_variance < self.min_z_variance:
            return {
                'verified': False,
                'distance': -1,
                'z_variance': z_variance,
                'reason': 'Flat signature (possible spoof)'
            }
        
        # Resample both paths to same length
        ref_len = len(self.reference_points)
        cand_len = len(candidate_path)
        target_len = min(ref_len, cand_len)
        
        ref_resampled = self._resample_path(self.reference_points, target_len)
        cand_points = np.array([[p['x'], p['y'], p['z']] for p in candidate_path])
        cand_resampled = self._resample_path(cand_points, target_len)
        
        # Compute average Euclidean distance
        distances = [euclidean(ref_resampled[i], cand_resampled[i]) for i in range(target_len)]
        avg_distance = np.mean(distances)
        
        threshold = self.threshold * threshold_multiplier
        verified = avg_distance <= threshold
        
        return {
            'verified': verified,
            'distance': float(avg_distance),
            'z_variance': float(z_variance),
            'reason': 'Match' if verified else f'Distance: {avg_distance:.2f} > {threshold}'
        }
    
    def _resample_path(self, points, target_length):
        """Resample path to target length using linear interpolation."""
        current_length = len(points)
        indices = np.linspace(0, current_length - 1, target_length)
        
        resampled = []
        for idx in indices:
            lower = int(np.floor(idx))
            upper = min(int(np.ceil(idx)), current_length - 1)
            weight = idx - lower
            
            if lower == upper:
                resampled.append(points[lower])
            else:
                interpolated = (1 - weight) * points[lower] + weight * points[upper]
                resampled.append(interpolated)
        
        return np.array(resampled)
    
    def update_threshold(self, new_threshold):
        """Update verification threshold."""
        self.threshold = new_threshold
        print(f"[Verifier] Threshold updated to: {new_threshold}")
