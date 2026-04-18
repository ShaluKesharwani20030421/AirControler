"""
3D Biometric Signature Recorder
Captures index finger tip (x, y, z) coordinates for 3 seconds to create
a unique 3D signature using Orbbec Gemini 335 depth data.
"""

import json
import time
import numpy as np
from pathlib import Path


class SignatureRecorder:
    """
    Records a 3D biometric signature by tracking index finger movement
    in 3D space (x, y, z) for a fixed duration.
    
    Anti-Spoofing:
    - Requires significant Z-axis variation (depth changes)
    - Rejects flat 2D signatures that could be video replays
    """
    
    def __init__(self, duration=3.0, min_z_variance=100.0):
        """
        Args:
            duration: Recording duration in seconds (default 3.0)
            min_z_variance: Minimum depth variance in mm to prevent spoofing
        """
        self.duration = duration
        self.min_z_variance = min_z_variance  # mm
        
        self.recording = False
        self.start_time = None
        self.signature_path = []
        
    def start_recording(self):
        """Begin signature recording."""
        self.recording = True
        self.start_time = time.time()
        self.signature_path = []
        print(f"[Signature] Recording started - draw your signature in 3D space for {self.duration}s")
    
    def add_point(self, hand_data):
        """
        Add a point to the signature path.
        
        Args:
            hand_data: Dictionary with index_tip coordinates
        
        Returns:
            bool: True if recording complete, False if still recording
        """
        if not self.recording:
            return False
        
        if hand_data is None:
            return False
        
        # Extract 3D coordinates
        tip = hand_data['index_tip']
        x = tip.get('x', 0)
        y = tip.get('y', 0)
        z = tip.get('z', 0)  # Depth in mm
        
        # Record point with timestamp
        elapsed = time.time() - self.start_time
        self.signature_path.append({
            'x': float(x),
            'y': float(y),
            'z': float(z),
            'timestamp': elapsed
        })
        
        # Check if recording complete
        if elapsed >= self.duration:
            self.recording = False
            return self._finalize_recording()
        
        return False
    
    def _finalize_recording(self):
        """
        Finalize recording and validate signature.
        
        Returns:
            bool: True if signature is valid, False if rejected
        """
        if len(self.signature_path) < 30:  # Need at least 30 points (~10 FPS)
            print(f"[Signature] REJECTED - Too few points: {len(self.signature_path)}")
            return False
        
        # Anti-spoofing: Check Z-axis variance
        z_values = [p['z'] for p in self.signature_path]
        z_variance = np.var(z_values)
        z_range = max(z_values) - min(z_values)
        
        print(f"[Signature] Z-variance: {z_variance:.1f} mm², Z-range: {z_range:.1f} mm")
        
        if z_variance < self.min_z_variance:
            print(f"[Signature] REJECTED - Flat signature (possible video spoof)")
            print(f"[Signature] Required Z-variance: {self.min_z_variance} mm², Got: {z_variance:.1f} mm²")
            return False
        
        print(f"[Signature] VALID - {len(self.signature_path)} points, Z-variance OK")
        return True
    
    def save_signature(self, filepath):
        """
        Save recorded signature to JSON file.
        
        Args:
            filepath: Path to save signature (e.g., 'signatures/user1.json')
        """
        if not self.signature_path:
            raise ValueError("No signature recorded")
        
        # Create directory if needed
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Compute signature metadata
        z_values = [p['z'] for p in self.signature_path]
        
        signature_data = {
            'version': '1.0',
            'recorded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': self.duration,
            'num_points': len(self.signature_path),
            'metadata': {
                'z_variance': float(np.var(z_values)),
                'z_range': float(max(z_values) - min(z_values)),
                'z_mean': float(np.mean(z_values)),
            },
            'path': self.signature_path
        }
        
        with open(filepath, 'w') as f:
            json.dump(signature_data, f, indent=2)
        
        print(f"[Signature] Saved to: {filepath}")
        print(f"[Signature] Points: {len(self.signature_path)}, Z-var: {signature_data['metadata']['z_variance']:.1f}")
    
    def get_progress(self):
        """
        Get recording progress.
        
        Returns:
            float: Progress from 0.0 to 1.0, or -1 if not recording
        """
        if not self.recording:
            return -1.0
        
        elapsed = time.time() - self.start_time
        return min(1.0, elapsed / self.duration)
    
    def cancel_recording(self):
        """Cancel current recording."""
        self.recording = False
        self.signature_path = []
        print("[Signature] Recording cancelled")
