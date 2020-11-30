//
//  MainVC.swift
//  AlzAppV2
//
//  Created by Wang on 2020/11/16.
//

import Foundation
import AVFoundation
import UIKit
class MainVC: UIViewController,AVAudioRecorderDelegate, AVAudioPlayerDelegate{
    var main_speakers:[(id: Int, name: String, relationship:String, photo:String)] = [(0,"New Speaker","Unknown","")]


    var audioString = ""
    var nameString = ""
    var relationshipString = ""
    var photoString = ""
    private var audioSession: AVAudioSession!
    private var audioRecorder: AVAudioRecorder!
    private var audioPlayer: AVAudioPlayer!
    private let audioFile = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("chatteraudio.m4a")
    private var didRecord = false
    enum StateMachine {
        case start, playing, recording, paused
    }
    private let recIcon = UIImage(systemName: "mic.circle")!
    private let recstopIcon = UIImage(systemName: "mic.circle.fill")!
    private var currState : StateMachine!
    
    @IBOutlet weak var collectButton: UIButton!
    @IBOutlet weak var communityButton: UIButton!
    @IBOutlet weak var recButton: UIButton!
    
    @IBOutlet weak var detailLabel: UILabel!
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
        fetchData()
        NotificationCenter.default.addObserver(self, selector: #selector(fetchAfterSubmit(_:)), name: Notification.Name(rawValue: "fetchAfterSubmit"), object: nil)

        
    }
    @objc func fetchAfterSubmit(_ notification: Notification) {
        DispatchQueue.main.async {
            self.collectButton.isEnabled = false
            self.communityButton.isEnabled = false
        }
        let delayTime = DispatchTime.now() + 1.5
        DispatchQueue.main.asyncAfter(deadline: delayTime, execute: {
            self.getSpeakers()
        })
    }
    func getSpeakers() {
        let requestURL = "https://161.35.116.242/getSpeakersV2/"
        var request = URLRequest(url: URL(string: requestURL)!)
        request.httpMethod = "GET"
        let task = URLSession.shared.dataTask(with: request) { (data, response, error) in
            do {
                self.main_speakers = [(0,"New Speaker","Unknown","")]
                let json = try JSONSerialization.jsonObject(with: data!) as! [String:Any]
                for speakerEntry in json["speakers"] as? [[Any]] ?? []{
                    print(speakerEntry)
                    self.main_speakers.append((speakerEntry[0] as! Int,speakerEntry[1] as! String, speakerEntry[2] as! String, speakerEntry[3] as! String))
                }

            } catch let error as NSError {
                print(error)
            }
            DispatchQueue.main.async {
                self.collectButton.isEnabled = true
                self.communityButton.isEnabled = true
            }
            
        }
        task.resume()
    }
    override func prepare(for segue: UIStoryboardSegue, sender: Any?)
    {
        if segue.identifier == "CollectSegue"{
            let collectVC = segue.destination as! CollectVC
            collectVC.speakers = main_speakers
        }
        if segue.identifier == "CommunitySegue"{
            let communityVC = segue.destination as! CommunityVC
            communityVC.speakers = main_speakers
        }
        if segue.identifier == "ResultSegue"{
            let resultVC = segue.destination as! ResultVC
            resultVC.nameString = nameString
            resultVC.relationshipString = relationshipString
            resultVC.photoString = photoString
        }

    }

    func fetchData(){
        DispatchQueue.main.async {
            self.collectButton.isEnabled = false
            self.communityButton.isEnabled = false
            
        }
        DispatchQueue.main.async {
            self.getSpeakers()
        }
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
            recButton.setImage(recIcon, for: .normal)
            recButton.isEnabled = false
            let json: [String: Any] = ["audio": audioString]
            let jsonData = try? JSONSerialization.data(withJSONObject: json)

            var request = URLRequest(url: URL(string: "https://161.35.116.242/identifyV2/")!)
            request.httpMethod = "POST"
            request.httpBody = jsonData

            let task = URLSession.shared.dataTask(with: request) { (data, response, error) in
                do {
                    let json = try JSONSerialization.jsonObject(with: data!) as! [String:String]
                    self.nameString = json["name"]!
                    self.relationshipString = json["relationship"]!
                    self.photoString = json["photo"]!
                    //let relationship = json["relationship"]!
                    
                    if !self.nameString.isEmpty{
                        DispatchQueue.main.async {
                            self.detailLabel.text = "I know who you are"
                            self.detailLabel.numberOfLines = 1
                            self.performSegue(withIdentifier: "ResultSegue", sender: nil)

                        }
                        
                    }else{
                        DispatchQueue.main.async {
                            self.detailLabel.text = "Idk who you are"
                            self.detailLabel.numberOfLines = 1
                        }
                    }

                    
                } catch let error as NSError {
                    print(error)
                }
                self.reset()
//                DispatchQueue.main.async {
//                    self.performSegue(withIdentifier: "resultSegue", sender: nil)
//                }
            
                
            }
            task.resume()

        }
    }

    @IBAction func recTapped(_ sender: Any) {
        if (currState == StateMachine.recording) {
            finishRecording(success: true)
        } else {
            startRecording()
        }
    }
    func reset(){
        audioString = ""
        currState = StateMachine.start
        prepareRecorder()
        DispatchQueue.main.async {
            //self.recButton.setImage(self.recIcon, for: .normal)
            self.recButton.isEnabled = true
        }
    }


}

