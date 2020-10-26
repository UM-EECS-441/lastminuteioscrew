//
//  IdentifyVC.swift
//  AlzApp
//
//  Created by Wang on 2020/10/26.
//

import Foundation
//
//  CollectVC.swift
//  AlzApp
//
//  Created by Wang on 2020/10/25.
//

import UIKit
import AVFoundation

class IdentifyVC: UIViewController,AVAudioRecorderDelegate, AVAudioPlayerDelegate{
    // Audio-related variables
    
    var audioString = ""
    private var audioSession: AVAudioSession!
    private var audioRecorder: AVAudioRecorder!
    private var audioPlayer: AVAudioPlayer!
    private let audioFile = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("chatteraudio.m4a")
    private var didRecord = false
    enum StateMachine {
        case start, playing, recording, paused
    }
    private var currState : StateMachine!
    @IBOutlet weak var recButton: UIButton!
    @IBOutlet weak var detailLabel: UILabel!
    private let recIcon = UIImage(systemName: "mic.circle")!
    private let recstopIcon = UIImage(systemName: "mic.circle.fill")!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        audioSession = AVAudioSession.sharedInstance()
        do {
            try audioSession.setCategory(.playAndRecord, mode: .default)
            try audioSession.setActive(true)
        } catch {
            // failed to record handler
            print("viewDidLoad: failed to setup session")
            dismiss(animated: true, completion: nil)
        }
        func audioRecorderEncodeErrorDidOccur(_ recorder: AVAudioRecorder, error: Error?) {
            print("Error encoding audio: \(error!.localizedDescription)")
            finishRecording(success: false)
            // don't dismiss in case user wants to record again
        }
        currState = StateMachine.start
        audioString = ""
        prepareRecorder()
        recButton.isEnabled = true

    }
    func prepareRecorder() {
        // check permission first
        audioSession.requestRecordPermission() { allowed in
            if !allowed {
                print("prepareRecorder: no permission to record")
                self.dismiss(animated: true, completion: nil)
            }
        }
        let settings = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 12000,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]
        do {
            audioRecorder = try AVAudioRecorder(url: audioFile, settings: settings)
            audioRecorder.delegate = self
        } catch {
            print("prepareRecorder: failed")
            dismiss(animated: true, completion: nil)
        }
    }
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
    }

    // Audio related functions


    func startRecording() {
        currState = StateMachine.recording
        recButton.setImage(recstopIcon, for: .normal)
        
        audioRecorder.record()
    }
    func finishRecording(success: Bool) {
        audioRecorder.stop()
        
        currState = StateMachine.start
        recButton.setImage(recIcon, for: .normal)

        if success != true {
            print("finishRecording: failed to record")
        } else {
            didRecord = true
            detailLabel.text = "Waiting for results"
            recButton.isHidden = true
        }
    }
    @IBAction func recTapped(_ sender: Any) {
        if (currState == StateMachine.recording) {
            finishRecording(success: true)
        } else {
            startRecording()
        }
    }
    
}
