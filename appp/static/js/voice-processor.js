// potential future use to process voice for easy user interaction
class VoiceProcessor extends AudioWorkletProcessor {
  constructor() {
      super();
      this._volume = 0;
      this._updateIntervalInMS = 25;
      this._nextUpdateFrame = this._updateIntervalInMS;

      this.port.onmessage = (event) => {
          if (event.data.updateInterval) {
              this._updateIntervalInMS = event.data.updateInterval;
          }
      };
  }

  process(inputs, outputs, parameters) {
      const input = inputs[0];
      const samples = input[0];

      let sum = 0;
      for (let i = 0; i < samples.length; i++) {
          sum += samples[i] * samples[i];
      }
      const rms = Math.sqrt(sum / samples.length);
      this._volume = Math.max(rms, this._volume * 0.95);

      this._nextUpdateFrame -= 128;
      if (this._nextUpdateFrame < 0) {
          this._nextUpdateFrame += this._updateIntervalInMS * sampleRate / 1000;
          this.port.postMessage(this._volume * 100);
      }

      return true;
  }
}

registerProcessor('voice-processor', VoiceProcessor);
